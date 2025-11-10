"use client";
import { useState } from "react";
import { api } from "@/lib/api";
import { useRouter } from "next/navigation";
import Link from "next/link";

export default function SignUpPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await api.post("/auth/register", { username, password });
      const res = await api.post("/auth/login", { username, password });
      localStorage.setItem("access_token", res.data.access_token);
      localStorage.setItem("refresh_token", res.data.refresh_token);
      document.cookie = `access_token=${res.data.access_token}; Path=/; Max-Age=${60 * 60}; SameSite=Lax`;
      router.replace("/employess");
    } catch (err: any) {
      setError(err?.response?.data?.error || "Sign up failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen flex items-center justify-center bg-zinc-50 dark:bg-black text-black dark:text-zinc-50">
      <form onSubmit={onSubmit} className="w-full max-w-sm rounded-lg border p-6 bg-white dark:bg-zinc-900">
        <h1 className="text-xl font-semibold mb-4">Create account</h1>
        {error && <div className="mb-3 text-red-600 text-sm">{error}</div>}
        <div className="mb-3">
          <label className="block text-sm mb-1">Username</label>
          <input className="w-full border rounded px-3 py-2" value={username} onChange={e => setUsername(e.target.value)} />
        </div>
        <div className="mb-4">
          <label className="block text-sm mb-1">Password</label>
          <input type="password" className="w-full border rounded px-3 py-2" value={password} onChange={e => setPassword(e.target.value)} />
        </div>
        <button disabled={loading || !username || !password} className="w-full bg-black text-white rounded py-2 disabled:opacity-50">
          {loading ? "Creating..." : "Sign up"}
        </button>
        <p className="mt-3 text-sm text-zinc-600 dark:text-zinc-400">
          Already have an account? <Link href="/login" className="underline">Sign in</Link>
        </p>
      </form>
    </main>
  );
}