"use client";

import { useState, useCallback } from "react";
import { useRouter, usePathname } from "next/navigation";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";

const LANGUAGES = [
  { value: "", label: "All languages" },
  { value: "en", label: "English" },
  { value: "pt", label: "Portuguese" },
  { value: "es", label: "Spanish" },
  { value: "fr", label: "French" },
  { value: "de", label: "German" },
  { value: "it", label: "Italian" },
];

type Props = {
  q: string;
  lang: string;
};

export default function CatalogFilters({ q, lang }: Props) {
  const router = useRouter();
  const pathname = usePathname();
  const [search, setSearch] = useState(q);

  const navigate = useCallback(
    (newQ: string, newLang: string) => {
      const params = new URLSearchParams();
      if (newQ) params.set("q", newQ);
      if (newLang) params.set("lang", newLang);
      const qs = params.toString();
      router.push(pathname + (qs ? `?${qs}` : ""));
    },
    [router, pathname],
  );

  function handleSearchSubmit(e: React.FormEvent) {
    e.preventDefault();
    navigate(search, lang);
  }

  function handleLangChange(e: React.ChangeEvent<HTMLSelectElement>) {
    navigate(search, e.target.value);
  }

  return (
    <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
      <form onSubmit={handleSearchSubmit} className="flex flex-1 gap-2">
        <Input
          type="search"
          placeholder="Search books…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="flex-1"
          aria-label="Search books"
        />
      </form>
      <Select
        value={lang}
        onChange={handleLangChange}
        className="sm:w-44"
        aria-label="Filter by language"
      >
        {LANGUAGES.map(({ value, label }) => (
          <option key={value} value={value}>
            {label}
          </option>
        ))}
      </Select>
    </div>
  );
}
