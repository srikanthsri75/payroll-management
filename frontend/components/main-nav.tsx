"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { Button } from "./ui/button";
import { useAuth } from "@/hooks/use-auth";

const MainNav = () => {
  const pathname = usePathname();
  const { isAuthenticated, logout } = useAuth();

  const routes = [
    {
      href: "/",
      label: "Dashboard",
      active: pathname === "/",
    },
    {
      href: "/employees",
      label: "Employees",
      active: pathname === "/employees",
    },
  ];

  return (
    <header className="border-b">
      <div className="flex h-16 items-center px-4">
        <nav className="flex items-center space-x-4 lg:space-x-6 mx-6">
          {routes.map((route) => (
            <Link
              key={route.href}
              href={route.href}
              className={cn(
                "text-sm font-medium transition-colors hover:text-primary",
                route.active
                  ? "text-black dark:text-white"
                  : "text-muted-foreground"
              )}
            >
              {route.label}
            </Link>
          ))}
        </nav>
        <div className="ml-auto flex items-center space-x-4">
          {isAuthenticated ? (
            <Button variant="outline" onClick={logout}>
              Sign out
            </Button>
          ) : (
            <>
              <Link href="/login">
                <Button variant="ghost" className="mr-2">
                  Login
                </Button>
              </Link>
              <Link href="/signup">
                <Button>Sign up</Button>
              </Link>
            </>
          )}
        </div>
      </div>
    </header>
  );
};

export default MainNav;
