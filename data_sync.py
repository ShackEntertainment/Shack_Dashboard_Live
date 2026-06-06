def load_live_exchange_data():
    """Load data from Google Sheets or return demo data with error message"""
    
    if not GOOGLE_SHEETS_AVAILABLE:
        demo_data = get_demo_data()
        return demo_data + ("Google Sheets libraries not installed",)
    
    try:
        creds = get_google_credentials()
        if not creds:
            demo_data = get_demo_data()
            if hasattr(st, 'secrets'):
                return demo_data + ("Credentials found but invalid. Check Secrets format.",)
            else:
                return demo_data + ("Credentials file not found. Running in demo mode.",)
        
        gc = gspread.authorize(creds)
        spreadsheet_name = st.secrets.get('connections', {}).get('gsheets', {}).get('spreadsheet', 'Shack_Live_Exchange_Master')
        
        try:
            spreadsheet = gc.open(spreadsheet_name)
        except gspread.exceptions.SpreadsheetNotFound:
            demo_data = get_demo_data()
            return demo_data + (f"Spreadsheet '{spreadsheet_name}' not found. Did you share it with shack-sa@shack-agent.iam.gserviceaccount.com?",)
        except gspread.exceptions.APIError as api_err:
            demo_data = get_demo_data()
            return demo_data + (f"API Error: {str(api_err)}. Check if spreadsheet is shared with service account.",)
        except Exception as e:
            demo_data = get_demo_data()
            return demo_data + (f"Error opening spreadsheet: {str(e)}",)
        
        try:
            events_sheet = spreadsheet.worksheet("01_Events")
            bookings_sheet = spreadsheet.worksheet("02_Bookings")
            artists_sheet = spreadsheet.worksheet("03_Artists")
            financials_sheet = spreadsheet.worksheet("04_Financials")
            ops_sheet = spreadsheet.worksheet("05_Operations_Log")
            snapshot_sheet = spreadsheet.worksheet("06_Snapshot")
            
            events_df = pd.DataFrame(events_sheet.get_all_records())
            bookings_df = pd.DataFrame(bookings_sheet.get_all_records())
            artists_df = pd.DataFrame(artists_sheet.get_all_records())
            financials_df = pd.DataFrame(financials_sheet.get_all_records())
            ops_df = pd.DataFrame(ops_sheet.get_all_records())
            
            snapshot_data = snapshot_sheet.get_all_values()
            snapshot_dict = {
                'quarter': snapshot_data[1][0] if len(snapshot_data) > 1 else 'N/A',
                'total_revenue': float(snapshot_data[1][1]) if len(snapshot_data) > 1 and snapshot_data[1][1] else 0.0,
                'total_expenses': float(snapshot_data[1][2]) if len(snapshot_data) > 1 and snapshot_data[1][2] else 0.0,
                'net_profit': float(snapshot_data[1][3]) if len(snapshot_data) > 1 and snapshot_data[1][3] else 0.0,
                'events_held': int(snapshot_data[1][4]) if len(snapshot_data) > 1 and snapshot_data[1][4] else 0,
                'total_attendees': int(snapshot_data[1][5]) if len(snapshot_data) > 1 and snapshot_data[1][5] else 0
            }
            
            return events_df, bookings_df, artists_df, financials_df, ops_df, snapshot_dict, None
            
        except gspread.exceptions.WorksheetNotFound as e:
            demo_data = get_demo_data()
            return demo_data + (f"Worksheet not found: {str(e)}. Make sure sheets are named 01_Events, 02_Bookings, etc.",)
        except Exception as e:
            demo_data = get_demo_data()
            return demo_data + (f"Error reading worksheets: {str(e)}",)
        
    except gspread.exceptions.APIError as e:
        demo_data = get_demo_data()
        return demo_data + (f"Google API Error: {str(e)}. Check credentials and permissions.",)
    except Exception as e:
        demo_data = get_demo_data()
        return demo_data + (f"Unexpected error: {str(e)}",)