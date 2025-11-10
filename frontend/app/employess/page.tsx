"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";

interface Employee {
  id: number;
  name: string;
  department: string;
  base_salary: number;
}

export default function EmployeesPage() {
  const [employees, setEmployees] = useState<Employee[]>([]);

  useEffect(() => {
    api.get("/employees").then(res => setEmployees(res.data));
  }, []);

  return (
    <main className="p-6">
      <h1 className="text-xl font-semibold mb-4">Employees</h1>
      <table className="border-collapse border border-gray-400 w-full">
        <thead>
          <tr className="bg-gray-100">
            <th className="border p-2">ID</th>
            <th className="border p-2">Name</th>
            <th className="border p-2">Department</th>
            <th className="border p-2">Salary</th>
          </tr>
        </thead>
        <tbody>
          {employees.map(e => (
            <tr key={e.id}>
              <td className="border p-2">{e.id}</td>
              <td className="border p-2">{e.name}</td>
              <td className="border p-2">{e.department}</td>
              <td className="border p-2">{e.base_salary}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </main>
  );
}
