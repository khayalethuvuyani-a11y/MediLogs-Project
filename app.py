# app.py
# pip install streamlit web3 streamlit-js-eval

import os
import time
import datetime
import json

import streamlit as st
from web3 import Web3
from streamlit_js_eval import streamlit_js_eval
import config

# --- set_page_config MUST be the very first Streamlit call ---
st.set_page_config(
    page_title=config.APP_NAME,
    page_icon="💊",
    layout="wide",
)

# =============================================================================
# BLOCKCHAIN CONNECTION
# =============================================================================
@st.cache_resource
def get_web3_and_contract():
    """Create one shared web3 + contract instance for the whole session."""
    _w3 = Web3(Web3.HTTPProvider(config.RPC_URL))
    try:
        _contract = _w3.eth.contract(
            address=Web3.to_checksum_address(config.CONTRACT_ADDRESS),
            abi=config.CONTRACT_ABI,
        )
    except Exception:
        _contract = None
    return _w3, _contract

w3, contract = get_web3_and_contract()

# =============================================================================
# SESSION STATE — wallet details persist across Streamlit reruns
# =============================================================================
if "wallet_address" not in st.session_state:
    st.session_state.wallet_address = None
if "wallet_chain_id" not in st.session_state:
    st.session_state.wallet_chain_id = None

# Passive wallet check on load — uses eth_accounts (no popup)
_check = streamlit_js_eval(
    js_expressions="""
        (async () => {
            if (typeof window.ethereum === 'undefined')
                return JSON.stringify({ addr: null, chain: null });
            try {
                const accounts = await window.ethereum.request({ method: 'eth_accounts' });
                const chainId  = await window.ethereum.request({ method: 'eth_chainId' });
                return JSON.stringify({ addr: accounts[0] || null, chain: chainId });
            } catch(e) {
                return JSON.stringify({ addr: null, chain: null });
            }
        })()
    """,
    key="passive_wallet_check",
)
if _check:
    try:
        _d = json.loads(_check)
        st.session_state.wallet_address  = _d.get("addr")
        st.session_state.wallet_chain_id = _d.get("chain")  # hex string e.g. "0xaa36a7"
    except Exception:
        pass

# =============================================================================
# HELPERS
# =============================================================================

def render_header():
    """Show logo OR app name (never both), then tagline and description."""
    shown = False
    if config.LOGO_PATH:
        try:
            if os.path.exists(config.LOGO_PATH):
                st.image(config.LOGO_PATH, width=180)
                shown = True
        except Exception:
            pass
    if not shown:
        st.title(config.APP_NAME)
    st.caption(config.TAGLINE)
    st.info(config.DESCRIPTION, icon="ℹ️")
    st.divider()


def wallet_ok() -> bool:
    """Return True only when MetaMask is connected AND on Sepolia."""
    addr  = st.session_state.wallet_address
    chain = st.session_state.wallet_chain_id
    if not addr:
        st.warning("Please connect your MetaMask wallet (see sidebar) to perform this action.")
        return False
    if chain and chain.lower() != config.TARGET_CHAIN_ID_HEX.lower():
        st.warning(
            f"MetaMask is on the wrong network ({chain}). "
            "Please switch to **Sepolia Testnet** and refresh."
        )
        return False
    return True


def status_label(code: int) -> str:
    return config.STATUS_LABELS.get(code, f"Unknown ({code})")


def status_color(code: int) -> str:
    return config.STATUS_COLORS.get(code, "gray")


def format_ts(unix_ts: int) -> str:
    """Convert a Unix timestamp to a readable date/time string."""
    try:
        return datetime.datetime.utcfromtimestamp(unix_ts).strftime("%d %B %Y, %H:%M UTC")
    except Exception:
        return "—"


def send_tx(fn_name: str, args: list):
    """
    Encode the contract call in Python, pass raw calldata to MetaMask
    for signing. The private key never touches the Python server.
    Returns the tx hash string, or None on failure.
    """
    if not wallet_ok():
        return None
    if not contract:
        st.error("Contract is not initialised — check config.py.")
        return None
    try:
        # encode_abi returns a hex string like "0xabcd..." safe to embed in JS
        calldata = contract.encode_abi(fn_name, args=args)
        js = f"""
        (async () => {{
            try {{
                const txHash = await window.ethereum.request({{
                    method: 'eth_sendTransaction',
                    params: [{{
                        from: '{st.session_state.wallet_address}',
                        to:   '{config.CONTRACT_ADDRESS}',
                        data: '{calldata}'
                    }}]
                }});
                return txHash;
            }} catch (err) {{
                return 'ERROR:' + err.message;
            }}
        }})()
        """
        # Unique key per call so Streamlit doesn't reuse a cached widget result
        result = streamlit_js_eval(js_expressions=js, key=f"tx_{fn_name}_{time.time()}")
        if result is None:
            return None
        if str(result).startswith("ERROR:"):
            st.error(f"MetaMask rejected the transaction: {result[6:]}")
            return None
        return result
    except Exception as e:
        st.error(f"Could not build transaction: {e}")
        return None


def show_tx(tx_hash):
    """Show a success banner with a clickable Etherscan link."""
    if tx_hash:
        st.success("Transaction submitted to the network!")
        st.markdown(f"[View on Sepolia Etherscan ↗]({config.ETHERSCAN_BASE}{tx_hash})")


# =============================================================================
# SIDEBAR — wallet panel + navigation
# =============================================================================
with st.sidebar:
    st.header(config.APP_NAME)
    st.divider()

    st.subheader("Wallet")
    addr  = st.session_state.wallet_address
    chain = st.session_state.wallet_chain_id

    if addr:
        st.success("Connected")
        st.code(f"{addr[:6]}...{addr[-4:]}", language=None)
        if chain and chain.lower() == config.TARGET_CHAIN_ID_HEX.lower():
            st.caption("✅ Sepolia Testnet")
        else:
            st.warning(f"Wrong network ({chain}). Switch to Sepolia.")
    else:
        st.info("Not connected")
        if st.button("Connect MetaMask", use_container_width=True):
            # Only trigger the MetaMask popup when the user explicitly clicks
            _res = streamlit_js_eval(
                js_expressions="""
                (async () => {
                    if (typeof window.ethereum === 'undefined')
                        return JSON.stringify({ addr: null, chain: null,
                            err: 'MetaMask not found. Please install the MetaMask browser extension.' });
                    try {
                        const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
                        const chainId  = await window.ethereum.request({ method: 'eth_chainId' });
                        return JSON.stringify({ addr: accounts[0] || null, chain: chainId });
                    } catch(e) {
                        return JSON.stringify({ addr: null, chain: null, err: e.message });
                    }
                })()
                """,
                key="connect_btn",
            )
            if _res:
                try:
                    _d = json.loads(_res)
                    if _d.get("err"):
                        st.error(_d["err"])
                    else:
                        st.session_state.wallet_address  = _d.get("addr")
                        st.session_state.wallet_chain_id = _d.get("chain")
                        st.rerun()
                except Exception:
                    st.error("Unexpected response from MetaMask.")

    st.divider()
    st.subheader("Navigation")
    page = st.radio(
        "Go to",
        options=[
            "📊 Dashboard",
            "🔍 Medication Tracker",
            "🚚 Supply Chain Actions",
            "📋 Audit",
            "👤 Role Management",
        ],
        label_visibility="collapsed",
    )


# =============================================================================
# PAGE: DASHBOARD
# =============================================================================
if page == "📊 Dashboard":
    render_header()
    st.subheader("System Overview")

    col1, col2 = st.columns(2)

    with col1:
        with st.spinner("Fetching total medications…"):
            try:
                # medicationCount() is the real function name in the deployed contract
                total = contract.functions.medicationCount().call()
                st.metric("Total Medications Registered", total)
            except Exception as e:
                st.error(f"Could not load total: {e}")

    with col2:
        try:
            block_num = w3.eth.block_number
            st.metric("Latest Sepolia Block", f"#{block_num:,}")
        except Exception as e:
            st.error(f"Network error: {e}")

    st.divider()
    st.subheader("Quick Medication Lookup")
    q_id = st.number_input("Medication ID", min_value=1, step=1, key="dash_id")
    if st.button("Look Up", key="dash_lookup"):
        with st.spinner(f"Fetching medication #{q_id}…"):
            try:
                # getMedicationDetails returns a tuple struct from the contract
                med = contract.functions.getMedicationDetails(q_id).call()
                # med = (id, name, batchNumber, status, currentHandler, timestamp)
                color = status_color(med[3])
                st.markdown(f"### {med[1]}")
                st.markdown(f"**Stage:** :{color}[{status_label(med[3])}]")
                c1, c2, c3 = st.columns(3)
                c1.metric("Medication ID",  med[0])
                c2.metric("Batch Number",   med[2])
                c3.metric("Last Updated",   format_ts(med[5]))
                st.caption(f"Current handler: `{med[4]}`")
            except Exception as e:
                st.error(f"Could not retrieve record: {e}")

    st.divider()
    st.caption(
        f"Contract: `{config.CONTRACT_ADDRESS}` on Sepolia — "
        f"[View on Etherscan ↗](https://sepolia.etherscan.io/address/{config.CONTRACT_ADDRESS})"
    )


# =============================================================================
# PAGE: MEDICATION TRACKER
# =============================================================================
elif page == "🔍 Medication Tracker":
    render_header()
    st.subheader("Medication Tracker")
    st.write("Look up the full details and lifecycle stage of any registered medication.")

    med_id = st.number_input("Medication ID", min_value=1, step=1, key="trk_id")
    if st.button("Retrieve Record"):
        with st.spinner(f"Fetching record #{med_id}…"):
            try:
                med = contract.functions.getMedicationDetails(med_id).call()
                # med = (id, name, batchNumber, status, currentHandler, timestamp)
                color = status_color(med[3])
                st.markdown(f"### {med[1]}")
                st.markdown(f"**Stage:** :{color}[{status_label(med[3])}]")
                st.divider()
                c1, c2 = st.columns(2)
                with c1:
                    st.metric("Medication ID",  med[0])
                    st.metric("Batch Number",   med[2])
                with c2:
                    st.metric("Last Updated",   format_ts(med[5]))
                    st.caption("Current handler")
                    st.code(med[4], language=None)
            except Exception as e:
                st.error(f"Unable to retrieve record: {e}")

    st.divider()
    st.subheader("Check a Staff Member's Role")
    role_addr = st.text_input("Wallet Address", placeholder="0x…", key="role_addr")
    st.caption("Enter the Ethereum wallet address of the staff member.")
    if st.button("Check Role"):
        if not role_addr:
            st.warning("Please enter a wallet address.")
        else:
            with st.spinner("Looking up role…"):
                try:
                    checksummed = Web3.to_checksum_address(role_addr)
                    # roles() mapping returns a plain string in the live contract
                    role_str = contract.functions.roles(checksummed).call()
                    if not role_str:
                        st.info("This address has no role assigned in MediLogs.")
                    else:
                        # Translate the raw role key to a friendly display label
                        display = next(
                            (label for label, key in config.ROLE_OPTIONS if key == role_str),
                            role_str  # fall back to the raw string if not in our list
                        )
                        st.success(f"Role: **{display}**")
                except ValueError:
                    st.error("Invalid Ethereum address — must start with 0x and be 42 characters.")
                except Exception as e:
                    st.error(f"Role lookup failed: {e}")


# =============================================================================
# PAGE: SUPPLY CHAIN ACTIONS
# =============================================================================
elif page == "🚚 Supply Chain Actions":
    render_header()
    st.subheader("Supply Chain Actions")
    st.write("Move a medication through each stage of its lifecycle. Each action requires the appropriate staff role.")

    action = st.selectbox("Choose an action", [
        "Register New Medication Batch",
        "Dispatch Medication",
        "Confirm Medication Received",
        "Verify Quality",
        "Issue to Ward",
        "Mark as Used",
    ])
    st.divider()

    # ── Register ──────────────────────────────────────────────────────────────
    if action == "Register New Medication Batch":
        st.markdown("#### Register a New Batch")
        st.write("Adds a new medication to the system. Requires an authorised role.")
        with st.form("reg_form"):
            r_name  = st.text_input("Medication Name",    placeholder="e.g. Amoxicillin 500mg")
            r_batch = st.text_input("Batch / Lot Number", placeholder="e.g. BN-2025-001")
            st.caption("Both fields are required. The batch number must be unique.")
            go = st.form_submit_button("Register on Blockchain")
        if go:
            if not r_name or not r_batch:
                st.warning("Please fill in both fields.")
            else:
                with st.spinner("Waiting for MetaMask confirmation…"):
                    # Live contract takes only (name, batchNumber) — no id/quantity/expiry
                    show_tx(send_tx("registerMedication", [r_name, r_batch]))

    # ── Dispatch ──────────────────────────────────────────────────────────────
    elif action == "Dispatch Medication":
        st.markdown("#### Dispatch a Batch")
        st.write("Marks a registered batch as dispatched from the distribution centre.")
        d_id = st.number_input("Medication ID", min_value=1, step=1, key="d_id")
        st.caption("The numeric ID assigned to this batch when it was registered.")
        if st.button("Confirm Dispatch"):
            with st.spinner("Waiting for MetaMask…"):
                show_tx(send_tx("dispatchMedication", [d_id]))

    # ── Receive ───────────────────────────────────────────────────────────────
    elif action == "Confirm Medication Received":
        st.markdown("#### Confirm Arrival at Hospital Warehouse")
        st.write("Acknowledges physical arrival of a dispatched batch.")
        rv_id = st.number_input("Medication ID", min_value=1, step=1, key="rv_id")
        st.caption("The numeric ID of the batch that has physically arrived.")
        if st.button("Confirm Receipt"):
            with st.spinner("Waiting for MetaMask…"):
                show_tx(send_tx("receiveMedication", [rv_id]))

    # ── Verify Quality ────────────────────────────────────────────────────────
    elif action == "Verify Quality":
        st.markdown("#### Quality Inspection")
        st.write("Records the outcome of a quality inspection. Requires Quality Inspector role.")
        qv_id = st.number_input("Medication ID", min_value=1, step=1, key="qv_id")
        st.caption("The numeric ID of the batch being inspected.")
        if st.button("Mark as Quality Verified"):
            with st.spinner("Waiting for MetaMask…"):
                show_tx(send_tx("verifyQuality", [qv_id]))

    # ── Issue to Ward ─────────────────────────────────────────────────────────
    elif action == "Issue to Ward":
        st.markdown("#### Issue Medication to Ward")
        st.write("Releases a verified batch for patient use in the ward.")
        iw_id = st.number_input("Medication ID", min_value=1, step=1, key="iw_id")
        st.caption("The numeric ID of the batch being issued.")
        if st.button("Issue to Ward"):
            with st.spinner("Waiting for MetaMask…"):
                show_tx(send_tx("issueToWard", [iw_id]))

    # ── Mark as Used ──────────────────────────────────────────────────────────
    elif action == "Mark as Used":
        st.markdown("#### Mark Medication as Used")
        st.write("Closes the lifecycle by confirming the medication was administered to a patient.")
        mu_id = st.number_input("Medication ID", min_value=1, step=1, key="mu_id")
        st.caption("The numeric ID of the batch that has been fully used.")
        if st.button("Mark as Used"):
            with st.spinner("Waiting for MetaMask…"):
                show_tx(send_tx("markAsUsed", [mu_id]))


# =============================================================================
# PAGE: AUDIT
# =============================================================================
elif page == "📋 Audit":
    render_header()
    st.subheader("Audit")
    st.write("Flag a medication batch for independent review. Requires Auditor role.")

    aud_id = st.number_input("Medication ID", min_value=1, step=1, key="aud_id")
    st.caption("The numeric ID of the medication batch to be audited.")
    if st.button("Submit Audit Flag"):
        with st.spinner("Waiting for MetaMask…"):
            show_tx(send_tx("auditMedication", [aud_id]))

    st.divider()
    st.subheader("View Medication Record")
    st.write("Read the current on-chain state of any medication — no wallet needed.")
    v_id = st.number_input("Medication ID", min_value=1, step=1, key="v_id")
    if st.button("Load Record", key="audit_view"):
        with st.spinner(f"Fetching record #{v_id}…"):
            try:
                med = contract.functions.getMedicationDetails(v_id).call()
                color = status_color(med[3])
                st.markdown(f"**{med[1]}** — Batch `{med[2]}`")
                st.markdown(f"Stage: :{color}[{status_label(med[3])}]")
                st.metric("Last Updated", format_ts(med[5]))
                st.caption(f"Current handler: `{med[4]}`")
            except Exception as e:
                st.error(f"Could not load record: {e}")


# =============================================================================
# PAGE: ROLE MANAGEMENT
# =============================================================================
elif page == "👤 Role Management":
    render_header()
    st.subheader("Role Management")
    st.write("Assign roles to staff wallet addresses. Requires Founder role.")

    st.markdown("#### Assign a Role")
    with st.form("role_form"):
        rm_addr  = st.text_input("Staff Member's Wallet Address", placeholder="0x…")
        st.caption("The Ethereum wallet address of the person receiving the role.")
        rm_label = st.selectbox("Role to Assign", config.ROLE_LABELS)
        st.caption(
            "Procurement Manager — registers & dispatches | "
            "Technical Manager — receives & issues | "
            "Quality Inspector — inspects | Auditor — audits | Founder — manages roles"
        )
        rm_go = st.form_submit_button("Assign Role on Blockchain")

    if rm_go:
        if not rm_addr:
            st.warning("Please enter a wallet address.")
        else:
            # Resolve the display label back to the raw role key string
            role_key = next((k for l, k in config.ROLE_OPTIONS if l == rm_label), None)
            if not role_key:
                st.error("Could not resolve the selected role.")
            else:
                try:
                    checksummed = Web3.to_checksum_address(rm_addr)
                    with st.spinner("Waiting for MetaMask…"):
                        # Live contract assignRole takes (address, string) — plain string role
                        show_tx(send_tx("assignRole", [checksummed, role_key]))
                except ValueError:
                    st.error("Invalid Ethereum address — must start with 0x.")
                except Exception as e:
                    st.error(f"Role assignment failed: {e}")

    st.divider()
    st.markdown("#### Look Up a Staff Member's Role")
    lk_addr = st.text_input("Wallet Address", placeholder="0x…", key="lk_addr")
    if st.button("Check Role"):
        if not lk_addr:
            st.warning("Please enter a wallet address.")
        else:
            with st.spinner("Looking up role…"):
                try:
                    checksummed = Web3.to_checksum_address(lk_addr)
                    role_str    = contract.functions.roles(checksummed).call()
                    if not role_str:
                        st.info("This address has no role in the MediLogs system.")
                    else:
                        display = next(
                            (label for label, key in config.ROLE_OPTIONS if key == role_str),
                            role_str
                        )
                        st.success(f"Current Role: **{display}**")
                except ValueError:
                    st.error("Invalid Ethereum address.")
                except Exception as e:
                    st.error(f"Lookup failed: {e}")
