import { redirect } from "next/navigation";
import { apiFetch, ApiError } from "@/lib/api";
import { getToken } from "@/lib/auth";
import { Card, CardContent } from "@/components/ui/card";
import CatalogFilters from "@/components/catalog-filters";

type BookOut = {
  id: string;
  isbn_13: string | null;
  title: string;
  subtitle: string | null;
  authors: string[];
  published_year: number | null;
  language: string | null;
  cover_url: string | null;
};

type PageProps = {
  searchParams: Promise<{ q?: string; lang?: string }>;
};

export default async function CatalogPage({ searchParams }: PageProps) {
  const { q, lang } = await searchParams;

  const token = await getToken();
  if (!token) {
    redirect("/login?from=/catalog");
  }

  const query = new URLSearchParams();
  if (q) query.set("search", q);
  if (lang) query.set("language", lang);
  const qs = query.toString();

  let books: BookOut[] = [];
  try {
    books = await apiFetch<BookOut[]>(`/books/${qs ? `?${qs}` : ""}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
  } catch (err) {
    if (err instanceof ApiError && err.status === 401) {
      redirect("/login?from=/catalog");
    }
    throw err;
  }

  return (
    <main className="min-h-screen bg-background">
      <div className="mx-auto max-w-7xl px-4 py-8">
        <h1 className="mb-6 text-2xl font-semibold tracking-tight">Library</h1>

        <CatalogFilters q={q ?? ""} lang={lang ?? ""} />

        {books.length === 0 ? (
          <p className="mt-12 text-center text-muted-foreground">
            No books found.
          </p>
        ) : (
          <div className="mt-6 grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6">
            {books.map((book) => (
              <BookCard key={book.id} book={book} />
            ))}
          </div>
        )}
      </div>
    </main>
  );
}

function BookCard({ book }: { book: BookOut }) {
  return (
    <Card className="overflow-hidden">
      <div className="aspect-[2/3] bg-muted">
        {book.cover_url ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={book.cover_url}
            alt={`Cover of ${book.title}`}
            className="h-full w-full object-cover"
          />
        ) : (
          <div className="flex h-full w-full items-center justify-center px-2">
            <span className="text-center text-xs text-muted-foreground line-clamp-3">
              {book.title}
            </span>
          </div>
        )}
      </div>
      <CardContent className="p-2">
        <p className="text-xs font-medium line-clamp-2">{book.title}</p>
        {book.authors.length > 0 && (
          <p className="text-xs text-muted-foreground line-clamp-1">
            {book.authors[0]}
          </p>
        )}
        {book.published_year !== null && (
          <p className="text-xs text-muted-foreground">{book.published_year}</p>
        )}
      </CardContent>
    </Card>
  );
}
