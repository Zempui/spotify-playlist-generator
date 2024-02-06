'use server'

import { ApiCallHandler } from "api/api";
import { NextRequest, NextResponse } from "next/server";

export async function GET(request: NextRequest) {
  const code = request.nextUrl.searchParams.get('code') ?? '';
  const apiCall = ApiCallHandler('/callback', 'get', {code: code}, {})
  await apiCall.fetch();
  const setCookies = apiCall.api.setCookies;

  var sessionValue = null;
  setCookies.forEach(function(cookie) {
    var cookieParts = cookie.split('=');
    var cookieName = cookieParts[0].trim();
    var cookieValue = cookieParts[1].trim();
    if (cookieName === 'session') {
        sessionValue = cookieValue;
    }
});
  const response = NextResponse.redirect(new URL('/', `http://${request.headers.get('host')}`));
  response.cookies.set('session', sessionValue ?? '');
  return response;
}
