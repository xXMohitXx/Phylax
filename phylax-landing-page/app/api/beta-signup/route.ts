import { NextRequest, NextResponse } from 'next/server';
import { google } from 'googleapis';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { name, email } = body;

    if (!name || !email) {
      return NextResponse.json(
        { error: 'Name and email are required' },
        { status: 400 }
      );
    }

    // Basic email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      return NextResponse.json(
        { error: 'Invalid email format' },
        { status: 400 }
      );
    }

    // We require credentials in the env variables to perform a secure server-to-server connection
    if (!process.env.GOOGLE_SERVICE_ACCOUNT_EMAIL || !process.env.GOOGLE_PRIVATE_KEY) {
      console.warn("⚠️ Missing Google Service Account credentials. Could not sync to Google Sheets.");
      console.log('Cloud Beta Signup Captured (Local):', { name, email, timestamp: new Date().toISOString() });
      
      // Still return success to the user so the UI updates
      return NextResponse.json(
        { success: true, message: 'Thanks for signing up for the Phylax Cloud beta! (Local dev fallback)' },
        { status: 200 }
      );
    }

    try {
      const auth = new google.auth.GoogleAuth({
        credentials: {
          client_email: process.env.GOOGLE_SERVICE_ACCOUNT_EMAIL,
          // Replace escaped newlines so the PEM key is parsed correctly
          private_key: process.env.GOOGLE_PRIVATE_KEY.replace(/\\n/g, '\n'),
        },
        scopes: ['https://www.googleapis.com/auth/spreadsheets'],
      });

      const sheets = google.sheets({ version: 'v4', auth });
      // The Spreadsheet ID extracted from the provided URL:
      const spreadsheetId = '1hkUllsrGi20Ubn-ngiVzAmwyZ7O3Nro_ivaiaLji1_w';
      const range = 'Sheet1!A:C'; // Assuming the headers are: Date, Name, Email

      await sheets.spreadsheets.values.append({
        spreadsheetId,
        range,
        valueInputOption: 'USER_ENTERED',
        requestBody: {
          values: [[new Date().toISOString(), name, email]],
        },
      });
    } catch (sheetError) {
      console.error('Google Sheets API Error:', sheetError);
      return NextResponse.json(
        { error: 'Internal server error while syncing waitlist' },
        { status: 500 }
      );
    }

    return NextResponse.json(
      { success: true, message: 'Thanks for signing up for the Phylax Cloud beta!' },
      { status: 200 }
    );
  } catch (error) {
    console.error('Api route parsing error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
