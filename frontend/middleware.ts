import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function middleware(req: NextRequest) {
    const { pathname } = req.nextUrl;
    const token = req.cookies.get("access_token")?.value;

    const isAuthPage = pathname.startsWith("/login") || pathname.startsWith("/signup");
    const isNextInternal = pathname.startsWith("/_next") || pathname === "/favicon.ico";

    // Allow Next internals always
    if (isNextInternal) return NextResponse.next();

    // Allow auth pages when not authenticated
    if (isAuthPage && !token) return NextResponse.next();

    // If visiting any other page without token -> redirect to /login
    if (!token && !isAuthPage) {
        const url = req.nextUrl.clone();
        url.pathname = "/login";
        url.searchParams.set("next", pathname);
        return NextResponse.redirect(url);
    }

    // If visiting auth pages while authenticated -> send to employees page
    if (isAuthPage && token) {
        const url = req.nextUrl.clone();
        url.pathname = "/employess";
        return NextResponse.redirect(url);
    }

    return NextResponse.next();
}

export const config = {
    matcher: ["/:path*"],
};