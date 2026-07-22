import { NextResponse } from "next/server";

const backendBaseUrl = process.env.BACKEND_URL || process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export async function GET() {
  try {
    const response = await fetch(`${backendBaseUrl}/history`);
    const data = await response.json().catch(() => null);

    if (!response.ok) {
      return NextResponse.json({ message: "History request failed", detail: data }, { status: response.status });
    }

    return NextResponse.json(data, { status: 200 });
  } catch (error) {
    return NextResponse.json(
      { message: error instanceof Error ? error.message : "History request failed" },
      { status: 500 }
    );
  }
}
