import streamlit as st
import pandas as pd
import os

# Import credentials logic from existing data_sync
try:
    from data_sync import get_google_credentials
    GOOGLE_SHEETS_AVAILABLE = True
except ImportError:
    GOOGLE_SHEETS_AVAILABLE = False
    def get_google_credentials():
        return None

try:
    import gspread
except ImportError:
    pass

def load_command_data():
    """Load data from Shack_Command_Center_Master"""
    
    if not GOOGLE_SHEETS_AVAILABLE:
        return (pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), {}, "Google Sheets libraries not installed")
    
    try:
        creds = get_google_credentials()
        if not creds:
            return (pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), {}, "Failed to load credentials.")
        
        gc = gspread.authorize(creds)
        
        try:
            spreadsheet = gc.open("Shack_Command_Center_Master")
        except Exception as e:
            return (pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), {}, f"Cannot find spreadsheet: {str(e)}")
        
        try:
            projects_df = pd.DataFrame(spreadsheet.worksheet("01_Project_Pipeline").get_all_records())
            kpi_df = pd.DataFrame(spreadsheet.worksheet("02_KPI_Tracker").get_all_records())
            team_df = pd.DataFrame(spreadsheet.worksheet("03_Team_Activity").get_all_records())
            
            # Read Snapshot
            snapshot_data = spreadsheet.worksheet("04_Snapshot").get_all_values()
            snapshot_dict = {}
            if len(snapshot_data) > 1:
                headers = snapshot_data[0]
                values = snapshot_data[1]
                snapshot_dict = dict(zip(headers, values))
            
            return projects_df, kpi_df, team_df, snapshot_dict, None
            
        except Exception as e:
            return (pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), {}, f"Error reading worksheets: {str(e)}")
            
    except Exception as e:
        return (pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), {}, f"Error: {str(e)}")