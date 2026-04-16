import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

const PROTECTED = [
  /^\/orders\/new$/,
  /^\/orders\/[^/]+\/edit$/,
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
  matcher: ["/orders/new", "/orders/:id/edit"],
};
