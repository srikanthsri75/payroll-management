"use client";
import { useEffect, useMemo, useState } from "react";
import { api } from "@/lib/api";

interface Employee {
    id: number;
    name: string;
    department: string;
    base_salary: number;
}

interface Payslip {
    id: number;
    month: string;
    gross: number;
    deductions: number;
    net: number;
}

export default function EmployeesPage() {
    const [employees, setEmployees] = useState<Employee[]>([]);
    const [loading, setLoading] = useState(false);

    // Add employee form state
    const [name, setName] = useState("");
    const [department, setDepartment] = useState("");
    const [baseSalary, setBaseSalary] = useState<number | "">("");
    const canSubmit = useMemo(() => name.trim() && baseSalary !== "" && Number(baseSalary) >= 0, [name, baseSalary]);

    // Selected employee for payslips panel
    const [selectedId, setSelectedId] = useState<number | null>(null);
    const [selected, setSelected] = useState<Employee | null>(null);
    const [payslips, setPayslips] = useState<Payslip[]>([]);
    const [month, setMonth] = useState("");
    const [genLoading, setGenLoading] = useState(false);

    const loadEmployees = async () => {
        const res = await api.get("/employees/");
        setEmployees(res.data);
    };

    useEffect(() => {
        loadEmployees();
    }, []);

    const handleAdd = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!canSubmit) return;
        setLoading(true);
        try {
            await api.post("/employees/", {
                name: name.trim(),
                department: department.trim(),
                base_salary: Number(baseSalary),
            });
            setName("");
            setDepartment("");
            setBaseSalary("");
            await loadEmployees();
        } finally {
            setLoading(false);
        }
    };

    const selectEmployee = async (id: number) => {
        setSelectedId(id);
        // fetch employee and their payslips
        const [empRes, slipsRes] = await Promise.all([
            api.get(`/employees/${id}`),
            api.get(`/payslips/employee/${id}`),
        ]);
        setSelected(empRes.data);
        setPayslips(slipsRes.data);
    };

    const generatePayslip = async () => {
        if (!selectedId) return;
        setGenLoading(true);
        try {
            await api.post(`/payslips/generate/${selectedId}`, month ? { month } : {});
            const slipsRes = await api.get(`/payslips/employee/${selectedId}`);
            setPayslips(slipsRes.data);
        } finally {
            setGenLoading(false);
        }
    };

    const downloadPdf = async (payslipId: number) => {
        const res = await api.get(`/payslips/${payslipId}/pdf`, { responseType: "blob" });
        const url = URL.createObjectURL(res.data);
        const a = document.createElement("a");
        a.href = url;
        a.download = `payslip_${payslipId}.pdf`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        URL.revokeObjectURL(url);
    };

    return (
        <main className="p-6 grid grid-cols-1 md:grid-cols-2 gap-6">
            <section>
                <h1 className="text-xl font-semibold mb-4">Employees</h1>

                <form onSubmit={handleAdd} className="mb-6 flex flex-col gap-3 max-w-md">
                    <div className="flex flex-col">
                        <label className="text-sm">Name</label>
                        <input className="border rounded px-2 py-1" value={name} onChange={e => setName(e.target.value)} />
                    </div>
                    <div className="flex flex-col">
                        <label className="text-sm">Department</label>
                        <input className="border rounded px-2 py-1" value={department} onChange={e => setDepartment(e.target.value)} />
                    </div>
                    <div className="flex flex-col">
                        <label className="text-sm">Base Salary</label>
                        <input type="number" className="border rounded px-2 py-1" value={baseSalary} onChange={e => setBaseSalary(e.target.value === "" ? "" : Number(e.target.value))} />
                    </div>
                    <button disabled={!canSubmit || loading} className="bg-black text-white rounded px-3 py-2 disabled:opacity-50 w-fit">
                        {loading ? "Adding..." : "Add Employee"}
                    </button>
                </form>

                <table className="border-collapse border border-gray-400 w-full">
                    <thead>
                        <tr className="bg-gray-100">
                            <th className="border p-2">ID</th>
                            <th className="border p-2">Name</th>
                            <th className="border p-2">Department</th>
                            <th className="border p-2">Salary</th>
                            <th className="border p-2">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {employees.map(e => (
                            <tr key={e.id} className="hover:bg-gray-50">
                                <td className="border p-2">{e.id}</td>
                                <td className="border p-2">{e.name}</td>
                                <td className="border p-2">{e.department}</td>
                                <td className="border p-2">{e.base_salary}</td>
                                <td className="border p-2">
                                    <button className="text-blue-600 underline" onClick={() => selectEmployee(e.id)}>View payslips</button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </section>

            <section>
                <h2 className="text-lg font-semibold mb-3">{selected ? `Payslips for ${selected.name}` : "Select an employee"}</h2>
                {selected && (
                    <div className="flex flex-col gap-4">
                        <div className="flex items-end gap-2">
                            <div className="flex flex-col">
                                <label className="text-sm">Month (optional)</label>
                                <input placeholder="e.g. November 2025" className="border rounded px-2 py-1" value={month} onChange={e => setMonth(e.target.value)} />
                            </div>
                            <button onClick={generatePayslip} disabled={genLoading} className="bg-black text-white rounded px-3 py-2 disabled:opacity-50">
                                {genLoading ? "Generating..." : "Generate Payslip"}
                            </button>
                        </div>
                        <table className="border-collapse border border-gray-400 w-full">
                            <thead>
                                <tr className="bg-gray-100">
                                    <th className="border p-2">ID</th>
                                    <th className="border p-2">Month</th>
                                    <th className="border p-2">Gross</th>
                                    <th className="border p-2">Deductions</th>
                                    <th className="border p-2">Net</th>
                                    <th className="border p-2">PDF</th>
                                </tr>
                            </thead>
                            <tbody>
                                {payslips.map(p => (
                                    <tr key={p.id}>
                                        <td className="border p-2">{p.id}</td>
                                        <td className="border p-2">{p.month}</td>
                                        <td className="border p-2">{p.gross}</td>
                                        <td className="border p-2">{p.deductions}</td>
                                        <td className="border p-2">{p.net}</td>
                                        <td className="border p-2">
                                            <button className="text-blue-600 underline" onClick={() => downloadPdf(p.id)}>Download</button>
                                        </td>
                                    </tr>
                                ))}
                                {payslips.length === 0 && (
                                    <tr><td className="border p-2 text-center" colSpan={6}>No payslips yet</td></tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                )}
            </section>
        </main>
    );
}
