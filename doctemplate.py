from datetime import datetime, timezone

class TicketDocument:
    def __init__(self):
        self.document_template = {
            # --- Tracking ---
            "sheet_row": None,              # Row number in Google Sheets (updated after insert)
            "ticket_id": None,              # Unique ticket ID e.g. "TICKET-0001"
            "status": "Open",               # Open, In Progress, Escalated, Closed ✅

            # --- Dates ---
            "ticket_open_date": None,       # datetime — set on creation ✅
            "ticket_closed_date": None,     # datetime — set when closed ✅
            "last_updated": None,           # datetime — updated on every change

            # --- Discord Info ---
            "discord_id": None,             # User's Discord ID (int)
            "discord_handle": None,         # User's Discord handle e.g. "johndoe" ✅
            "discord_display_name": None,   # User's display name

            # --- Ticket Info ---
            "initial_concern": None,        # First message/problem by user
            "wallet_address": None,         # Wallet address if applicable
            "email_address": None,          # Email if applicable

            # --- Mod Actions ---
            "ticket_responded_by": None,    # Mod who first responded ✅
            "ticket_closed_by": None,       # Mod who closed the ticket ✅
            "escalated": False,             # Whether ticket was escalated 
            "escalated_to": None,           # Who it was escalated to

            # --- Remarks ---
            "remarks_escalation": None,     # Remarks if any team escalations were made
            "remarks_user_info": None,      # Pertinent info provided by the user
            "internal_notes": None,         # Private mod notes (not synced to Sheets)

            # --- Metadata ---
            "synced_to_sheets": False,      # Whether it has been pushed to Google Sheets
            "created_at":None
        }

#After pressing submit by user - kick if done twice within 5 minutes
#Bot can send the initial info as a discord message. Info gathered: wallet, email. 
#/log command by admins - can obtain the info from bot's message at any time.

needed = { 
    "ticket_open_date": None 
    "ticket_closed_date": None,
    "discord_handle": None, # Discord Info
    "ticket_responded_by": None,
    "ticket_closed_by": None,
    "wallet_address": None,
    "email_address": None,
    "remarks": None,
    "synced_to_sheets": False, #Gsheets, #bool 
    "sheet_row": None,
    "ticket_id": None,
    "status": "Open"
}