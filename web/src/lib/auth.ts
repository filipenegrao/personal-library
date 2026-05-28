"use server";

import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { apiFetch, ApiError } from "./api";

const COOKIE_NAME = "access_token";

export async function login(username: string, password: string): Promise<void> {
  let data: { access_token: string };
  try {
    data = await apiFetch<{ access_token: string }>("/auth/login", {
      method: "POST",
      body: { username, password },
    });
  } catch (err) {
    if (err instanceof ApiError && err.status === 401) {
      throw new Error("Invalid credentials");
    }
    throw new Error("Login failed. Please try again.");
  }

  const store = await cookies();
  store.set(COOKIE_NAME, data.access_token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
    path: "/",
    maxAge: 60 * 60 * 24 * 7,
  });
}

export async function logout(): Promise<void> {
  const store = await cookies();
  store.delete(COOKIE_NAME);
  redirect("/login");
}

export async function getToken(): Promise<string | undefined> {
  const store = await cookies();
  return store.get(COOKIE_NAME)?.value;
}
