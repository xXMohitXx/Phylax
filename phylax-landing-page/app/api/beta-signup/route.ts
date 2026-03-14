import { NextRequest, NextResponse } from 'next/server';

const GOOGLE_SHEETS_URL = process.env.GOOGLE_SHEETS_WEBHOOK_URL;

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

    // If Google Sheets webhook URL is configured, send data there
    if (GOOGLE_SHEETS_URL) {
      try {
        await fetch(GOOGLE_SHEETS_URL, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            name,
            email,
            timestamp: new Date().toISOString(),
            source: 'phylax-landing-page',
          }),
        });
      } catch (sheetError) {
        // Log but don't fail the user-facing request
        console.error('Google Sheets webhook error:', sheetError);
      }
    } else {
      // Fallback: log to console when no webhook is configured
      console.log('Cloud Beta Signup:', { name, email, timestamp: new Date().toISOString() });
    }

    return NextResponse.json(
      { success: true, message: 'Thanks for signing up for the Phylax Cloud beta!' },
      { status: 200 }
    );
  } catch {
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
