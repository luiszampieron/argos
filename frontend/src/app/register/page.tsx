"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { register } from "@/lib/api";
import { ApiError } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";

export default function RegisterPage() {
  const { login } = useAuth();
  const router = useRouter();
  const [form, setForm] = useState({
    name: "",
    email: "",
    cargo: "",
    password: "",
  });
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await register(form);
      await login(form.email, form.password);
      router.push("/dashboard");
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError("Erro inesperado. Tente novamente.");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex">
      {/* Left panel */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-violet-600 via-indigo-600 to-blue-500 flex-col justify-between p-12 text-white">
        <div>
          <span className="text-2xl font-bold tracking-tight">Argos</span>
        </div>
        <div>
          <p className="text-4xl font-bold leading-snug mb-4">
            Comece a organizar
            <br />
            seu time hoje.
          </p>
          <p className="text-indigo-200 text-lg">
            Crie sua conta em menos de 1 minuto.
          </p>
        </div>
        <p className="text-indigo-300 text-sm">© 2026 Argos</p>
      </div>

      {/* Right panel — form */}
      <div className="flex-1 flex items-center justify-center px-6 py-12 bg-slate-50">
        <div className="w-full max-w-sm">
          <div className="mb-8">
            <span className="lg:hidden text-2xl font-bold text-indigo-600">
              Argos
            </span>
            <h1 className="text-2xl font-bold text-slate-900 mt-4">
              Criar conta
            </h1>
            <p className="text-slate-500 mt-1 text-sm">
              Preencha os dados abaixo
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded-xl px-4 py-3 flex items-start gap-2">
                <span className="mt-0.5">⚠</span>
                <span>{error}</span>
              </div>
            )}

            {(
              [
                {
                  key: "name",
                  label: "Nome completo",
                  type: "text",
                  placeholder: "João Silva",
                },
                {
                  key: "email",
                  label: "E-mail",
                  type: "email",
                  placeholder: "joao@empresa.com",
                },
                {
                  key: "cargo",
                  label: "Cargo",
                  type: "text",
                  placeholder: "Desenvolvedor",
                },
                {
                  key: "password",
                  label: "Senha",
                  type: "password",
                  placeholder: "Mínimo 8 caracteres",
                },
              ] as const
            ).map(({ key, label, type, placeholder }) => (
              <div key={key} className="space-y-1.5">
                <label
                  className="text-sm font-medium text-slate-700"
                  htmlFor={key}
                >
                  {label}
                </label>
                <input
                  id={key}
                  name={key}
                  type={type}
                  required
                  value={form[key]}
                  onChange={handleChange}
                  placeholder={placeholder}
                  className="w-full bg-white border border-slate-200 rounded-xl px-4 py-2.5 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent shadow-sm transition"
                />
              </div>
            ))}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-indigo-600 hover:bg-indigo-700 active:scale-[.98] disabled:opacity-50 text-white font-semibold py-2.5 rounded-xl text-sm transition-all shadow-sm mt-2"
            >
              {loading ? "Cadastrando..." : "Criar conta"}
            </button>
          </form>

          <p className="text-center text-sm text-slate-500 mt-6">
            Já tem conta?{" "}
            <Link
              href="/login"
              className="text-indigo-600 hover:text-indigo-700 font-semibold"
            >
              Entrar
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
