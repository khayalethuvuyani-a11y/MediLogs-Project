# config.py
"""
Configuration File for MediLogs Prototype

SECTIONS:
  1. APPLICATION DISPLAY  — name, tagline, description shown in the UI
  2. NETWORK SETTINGS     — Sepolia RPC endpoint and chain ID
  3. SMART CONTRACT INFO  — address and ABI copied directly from Etherscan
  4. DATA DICTIONARIES    — human-readable labels for status codes and roles
  5. TEAM MEMBERS         — authorised wallet addresses mapped to names and roles
"""

# --- 1. APPLICATION DISPLAY ---
APP_NAME    = "MediLogs"
TAGLINE     = "Healthcare Supply Chain Tracker"
DESCRIPTION = (
    "A transparent, verifiable, and permanent tracking system for the "
    "medication lifecycle — preventing theft and ensuring accountability."
)
LOGO_PATH = "logo.jpeg" # replace with your actual filename

# --- 2. NETWORK SETTINGS ---
RPC_URL = "https://ethereum-sepolia-rpc.publicnode.com"

# Chain ID in both forms:
#   HEX — MetaMask returns chainId as a hex string e.g. "0xaa36a7"
#   INT — web3.py uses the integer form
TARGET_CHAIN_ID_HEX = "0xaa36a7"
TARGET_CHAIN_ID_INT = 11155111

# --- 3. SMART CONTRACT INFO ---
CONTRACT_ADDRESS = "0xC305c8929036A9855433a63Fc38714dAe59cae5B"

# ABI copied verbatim from Etherscan — this is the ground-truth interface
# of the contract actually deployed on Sepolia. Do not edit these entries.
#
# KEY DIFFERENCES from the Solidity source shared earlier — the live contract:
#   - Uses  medicationCount()  not  totalMedications()
#   - Uses  roles(address)     not  userRoles(address)  (stores plain strings, not bytes32)
#   - Uses  issueToWard(id)    not  issueMedication(id, amount)
#   - Uses  auditMedication(id) not  performAudit(id, count, notes)
#   - Uses  getMedicationDetails(id) for full record lookup
#   - registerMedication takes only (name, batchNumber) — no id/quantity/expiry
#   - assignRole takes (address, string) — role is a plain string, not bytes32
CONTRACT_ABI = [
    {
        "inputs": [],
        "stateMutability": "nonpayable",
        "type": "constructor"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "uint256",
                "name": "medicationId",
                "type": "uint256"
            },
            {
                "indexed": False,
                "internalType": "enum MediLogs.MedicationStatus",
                "name": "status",
                "type": "uint8"
            },
            {
                "indexed": True,
                "internalType": "address",
                "name": "actor",
                "type": "address"
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "time",
                "type": "uint256"
            }
        ],
        "name": "ActionLogged",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "address",
                "name": "account",
                "type": "address"
            },
            {
                "indexed": False,
                "internalType": "string",
                "name": "role",
                "type": "string"
            }
        ],
        "name": "RoleAssigned",
        "type": "event"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "_user",
                "type": "address"
            },
            {
                "internalType": "string",
                "name": "_role",
                "type": "string"
            }
        ],
        "name": "assignRole",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "uint256",
                "name": "_id",
                "type": "uint256"
            }
        ],
        "name": "auditMedication",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "uint256",
                "name": "_id",
                "type": "uint256"
            }
        ],
        "name": "dispatchMedication",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "uint256",
                "name": "_id",
                "type": "uint256"
            }
        ],
        "name": "getMedicationDetails",
        "outputs": [
            {
                "components": [
                    {
                        "internalType": "uint256",
                        "name": "id",
                        "type": "uint256"
                    },
                    {
                        "internalType": "string",
                        "name": "name",
                        "type": "string"
                    },
                    {
                        "internalType": "string",
                        "name": "batchNumber",
                        "type": "string"
                    },
                    {
                        "internalType": "enum MediLogs.MedicationStatus",
                        "name": "status",
                        "type": "uint8"
                    },
                    {
                        "internalType": "address",
                        "name": "currentHandler",
                        "type": "address"
                    },
                    {
                        "internalType": "uint256",
                        "name": "timestamp",
                        "type": "uint256"
                    }
                ],
                "internalType": "struct MediLogs.Medication",
                "name": "",
                "type": "tuple"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            }
        ],
        "name": "inventory",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "id",
                "type": "uint256"
            },
            {
                "internalType": "string",
                "name": "name",
                "type": "string"
            },
            {
                "internalType": "string",
                "name": "batchNumber",
                "type": "string"
            },
            {
                "internalType": "enum MediLogs.MedicationStatus",
                "name": "status",
                "type": "uint8"
            },
            {
                "internalType": "address",
                "name": "currentHandler",
                "type": "address"
            },
            {
                "internalType": "uint256",
                "name": "timestamp",
                "type": "uint256"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "uint256",
                "name": "_id",
                "type": "uint256"
            }
        ],
        "name": "issueToWard",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "uint256",
                "name": "_id",
                "type": "uint256"
            }
        ],
        "name": "markAsUsed",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "medicationCount",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "uint256",
                "name": "_id",
                "type": "uint256"
            }
        ],
        "name": "receiveMedication",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "string",
                "name": "_name",
                "type": "string"
            },
            {
                "internalType": "string",
                "name": "_batchNumber",
                "type": "string"
            }
        ],
        "name": "registerMedication",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "",
                "type": "address"
            }
        ],
        "name": "roles",
        "outputs": [
            {
                "internalType": "string",
                "name": "",
                "type": "string"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "uint256",
                "name": "_id",
                "type": "uint256"
            }
        ],
        "name": "verifyQuality",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

# --- 4. DATA DICTIONARIES ---

# Maps the MedicationStatus enum integer to plain English.
# Order matches the enum in the deployed contract.
STATUS_LABELS = {
    0: "Registered — Awaiting Dispatch",
    1: "Dispatched — In Transit",
    2: "Received — At Hospital Warehouse",
    3: "Quality Verified — Passed Inspection",
    4: "Issued to Ward",
    5: "Marked as Used",
    6: "Under Audit",
    7: "Closed — Lifecycle Complete / Rejected",
    8: "Expired — Unsafe for Use",
}

# Maps status codes to Streamlit colour tags for visual cues
STATUS_COLORS = {
    0: "blue",
    1: "orange",
    2: "blue",
    3: "green",
    4: "violet",
    5: "gray",
    6: "orange",
    7: "gray",
    8: "red",
}

# Role options — (display label, raw string passed to the contract).
# The live contract stores roles as plain strings, not keccak hashes.
ROLE_OPTIONS = [
    ("Founder",             "FOUNDER"),
    ("CEO",                 "CEO"),
    ("Procurement Manager", "PROCUREMENT_MANAGER"),
    ("Technical Manager",   "TECHNICAL_MANAGER"),
    ("Auditor",             "AUDITOR"),
    ("Quality Inspector",   "QUALITY_INSPECTOR"),
]

# Flat list of display labels — used by st.selectbox in the UI
ROLE_LABELS = [label for label, _ in ROLE_OPTIONS]

# Etherscan base URL — append a tx hash to build a clickable link
ETHERSCAN_BASE = "https://sepolia.etherscan.io/tx/"

# --- 5. TEAM MEMBERS ---
# Authorised wallet addresses mapped to member details.
# Keys are checksummed addresses (mixed-case EIP-55 format).
# The contract role string matches the raw values in ROLE_OPTIONS above.
#
# Usage example in your app:
#   member = TEAM_MEMBERS.get(Web3.to_checksum_address(connected_address))
#   if member:
#       st.success(f"Welcome, {member['name']} — {member['display_role']}")

TEAM_MEMBERS = {
    # Andile Duma — Procurement Manager
    "0xf061B4Ad458cE89D95dEb62bEA1C552e5CD99588": {
        "name":         "Andile Duma",
        "display_role": "Procurement Manager",
        "contract_role": "PROCUREMENT_MANAGER",
    },
    # Asanda Mabaso — Chief Executive Officer
    "0x56C2630824Aa36c70e7Ad1ef989cd1DFA26c9DFA": {
        "name":         "Asanda Mabaso",
        "display_role": "Chief Executive Officer",
        "contract_role": "CEO",
    },
    # Vuyani Magagula — Founder
    "0x2Dd586b00BF04281D2C14Cca4F46D7fB31f47c59": {
        "name":         "Vuyani Magagula",
        "display_role": "Founder",
        "contract_role": "FOUNDER",
    },
    # Thabang Makgalemele — Auditor
    "0xF3bBA1f93DF078BFa6FC2bdC184294D9165F61C2": {
        "name":         "Thabang Makgalemele",
        "display_role": "Auditor",
        "contract_role": "AUDITOR",
    },
    # Siboniso Sangweni — Quality Inspector
    "0x777Fc84933d4C2f7d78864afe2C466f515161CbC": {
        "name":         "Siboniso Sangweni",
        "display_role": "Quality Inspector",
        "contract_role": "QUALITY_INSPECTOR",
    },
    # Lesley Ramahlo — Technical Manager
    "0xbCE1DaDEddEDd437B8c691967F6f3d4c4459cb53": {
        "name":         "Lesley Ramahlo",
        "display_role": "Technical Manager",
        "contract_role": "TECHNICAL_MANAGER",
    },
}

def get_member_by_address(address: str) -> dict | None:
    """
    Look up a team member by their connected MetaMask address.

    Accepts any casing — normalises to EIP-55 checksum before lookup.
    Returns the member dict  { name, display_role, contract_role }
    or None if the address is not in the authorised list.

    Example
    -------
    from web3 import Web3
    member = get_member_by_address(web3.eth.accounts[0])
    if member:
        st.success(f"Welcome {member['name']} ({member['display_role']})")
    else:
        st.error("Address not recognised — contact the Founder to be added.")
    """
    try:
        from web3 import Web3
        checksum = Web3.to_checksum_address(address)
    except Exception:
        return None
    return TEAM_MEMBERS.get(checksum)
