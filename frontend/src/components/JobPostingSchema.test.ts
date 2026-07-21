import { describe, it, expect } from 'vitest';
import { experimental_AstroContainer as AstroContainer } from 'astro/container';
import JobPostingSchema from './JobPostingSchema.astro';

describe('JobPostingSchema', () => {
  it('should render valid JSON-LD for Google Jobs', async () => {
    const container = await AstroContainer.create();
    
    const jobProps = {
      title: "Product Design Intern",
      description: "A great role.",
      datePosted: "2024-01-01T00:00:00.000Z",
      employmentType: "INTERN" as const,
      hiringOrganization: {
        name: "Lumina Tech"
      },
      jobLocation: {
        addressCountry: "US",
        addressLocality: "San Francisco",
        addressRegion: "CA"
      }
    };

    const result = await container.renderToString(JobPostingSchema, {
      props: jobProps,
    });

    // Check if script tag is there
    expect(result).toContain('<script type="application/ld+json">');

    // Extract the JSON-LD
    const regex = /<script type="application\/ld\+json">(.*?)<\/script>/s;
    const match = result.match(regex);
    expect(match).toBeTruthy();

    if (match) {
      const jsonLd = JSON.parse(match[1]);
      expect(jsonLd['@context']).toBe('https://schema.org/');
      expect(jsonLd['@type']).toBe('JobPosting');
      expect(jsonLd.title).toBe(jobProps.title);
      expect(jsonLd.hiringOrganization.name).toBe(jobProps.hiringOrganization.name);
      expect(jsonLd.jobLocation.address.addressCountry).toBe(jobProps.jobLocation.addressCountry);
    }
  });
});
