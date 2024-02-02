'use server'

import { ApiCallHandler } from "api/api";
import { NextRequest, NextResponse } from "next/server";

export async function GET(request: NextRequest) {
  const code = request.nextUrl.searchParams.get('code') ?? '';
  const apiCall = ApiCallHandler('/callback', 'get', {code: code}, {})
  await apiCall.fetch();
  const response = NextResponse.redirect(new URL('/', request.url));
  response.cookies.set('code', code);
  return response;
}
