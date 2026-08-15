import { describe, it, expect, vi } from "vitest";
import { experimental_AstroContainer as AstroContainer } from "astro/container";
import JobDetailPage from "./[id].astro";

vi.mock("../../lib/api", () => ({
  fetchJob: vi.fn().mockResolvedValue({
    id: "job-abc-123",
    title: "Estágio em Desenvolvimento de Software",
    company: "Tech Start",
    location: "São Paulo, SP",
    modality: "REMOTE",
    area: "TI_SOFTWARE",
    description: "<p>Venha programar conosco</p>",
    salary: "R$ 3.000/mês",
    company_logo: "https://exemplo.com/logo.png",
    source_url: "https://gupy.io/vaga/123",
    source_name: "Gupy",
    posted_at: "2026-08-10T10:00:00Z",
    is_new: true,
  }),
}));

describe("Vagas [id] Page", () => {
  it("renders the 'Salvar no Tracker' button with proper data attributes and icons", async () => {
    const container = await AstroContainer.create();

    const html = await container.renderToString(JobDetailPage, {
      params: { id: "job-abc-123" },
    });

    expect(html).toContain('id="save-tracker-btn"');
    expect(html).toContain("Salvar no Tracker");
    expect(html).toContain("bookmark_add");
    expect(html).toContain('data-job-title="Estágio em Desenvolvimento de Software"');
    expect(html).toContain('data-job-company="Tech Start"');
  });

  it("renders the Tracker Toast popup with link to /tracker and close button", async () => {
    const container = await AstroContainer.create();

    const html = await container.renderToString(JobDetailPage, {
      params: { id: "job-abc-123" },
    });

    expect(html).toContain('id="tracker-toast"');
    expect(html).toContain("Vaga salva no Tracker!");
    expect(html).toContain('href="/tracker"');
    expect(html).toContain("Ver no Tracker");
    expect(html).toContain('id="tracker-toast-dismiss-x"');
  });
});
