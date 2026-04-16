import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

const PROTECTED = [
  /^\/dashboard\/new$/,
  /^\/dashboard\/[^/]+\/edit$/,
];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const isProtected = PROTECTED.some((pattern) => pattern.test(pathname));

  if (isProtected) {
    const token = request.cookies.get("auth_token")?.value;
    if (!token) {
      return NextResponse.redirect(new URL("/login", request.url));
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/dashboard/new", "/dashboard/:id/edit"],
};
