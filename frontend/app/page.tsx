"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";

interface Summary {
  total_employees: number;
  total_payslips: number;
  month_net_total: number;
}

interface ByMonthItem { month: string; net_total: number }
interface ByDeptItem { department: string; net_total: number }

export default function Home() {
  const [summary, setSummary] = useState<Summary | null>(null);
  const [byMonth, setByMonth] = useState<ByMonthItem[]>([]);
  const [byDept, setByDept] = useState<ByDeptItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const [s, m, d] = await Promise.all([
          api.get("/analytics/summary"),
          api.get("/analytics/payroll_by_month", { params: { months: 6 } }),
          api.get("/analytics/payroll_by_department"),
        ]);
        setSummary(s.data);
        setByMonth(m.data);
        setByDept(d.data);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  return (
    <main className="min-h-screen bg-zinc-50 dark:bg-black text-black dark:text-zinc-50">
      <div className="mx-auto max-w-5xl px-6 py-10">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-3xl font-semibold">Payroll Dashboard</h1>
            <p className="text-zinc-600 dark:text-zinc-400">Overview of employees and payroll activity</p>
          </div>
          <Link href="/employess" className="inline-flex items-center justify-center rounded-md bg-black text-white px-4 py-2 h-9">
            Go to Employees
          </Link>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
          <div className="rounded-lg border p-4">
            <div className="text-sm text-zinc-600">Total Employees</div>
            <div className="text-2xl font-semibold">{loading ? "—" : summary?.total_employees ?? 0}</div>
          </div>
          <div className="rounded-lg border p-4">
            <div className="text-sm text-zinc-600">Total Payslips</div>
            <div className="text-2xl font-semibold">{loading ? "—" : summary?.total_payslips ?? 0}</div>
          </div>
          <div className="rounded-lg border p-4">
            <div className="text-sm text-zinc-600">This Month Net Total</div>
            <div className="text-2xl font-semibold">{loading ? "—" : (summary ? summary.month_net_total.toLocaleString() : 0)}</div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="rounded-lg border p-4">
            <h2 className="font-semibold mb-3">Payroll by Month</h2>
            <table className="w-full text-sm border-collapse">
              <thead>
                <tr className="text-left">
                  <th className="border-b py-2 pr-2">Month</th>
                  <th className="border-b py-2">Net Total</th>
                </tr>
              </thead>
              <tbody>
                {loading && (
                  <tr><td className="py-3 text-zinc-500" colSpan={2}>Loading…</td></tr>
                )}
                {!loading && byMonth.length === 0 && (
                  <tr><td className="py-3 text-zinc-500" colSpan={2}>No data</td></tr>
                )}
                {byMonth.map((r) => (
                  <tr key={r.month}>
                    <td className="py-2 pr-2">{r.month}</td>
                    <td className="py-2">{r.net_total.toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="rounded-lg border p-4">
            <h2 className="font-semibold mb-3">Payroll by Department (This Month)</h2>
            <table className="w-full text-sm border-collapse">
              <thead>
                <tr className="text-left">
                  <th className="border-b py-2 pr-2">Department</th>
                  <th className="border-b py-2">Net Total</th>
                </tr>
              </thead>
              <tbody>
                {loading && (
                  <tr><td className="py-3 text-zinc-500" colSpan={2}>Loading…</td></tr>
                )}
                {!loading && byDept.length === 0 && (
                  <tr><td className="py-3 text-zinc-500" colSpan={2}>No data</td></tr>
                )}
                {byDept.map((r) => (
                  <tr key={r.department}>
                    <td className="py-2 pr-2">{r.department}</td>
                    <td className="py-2">{r.net_total.toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </main>
  );
}
