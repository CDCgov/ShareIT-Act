[![Run Status](https://img.shields.io/github/actions/workflow/status/cdcgov/shareit-act/create-code-json.yml?style=for-the-badge)](https://github.com/CDCgov/ShareIT-Act/actions/workflows/create-code-json.yml)
[![Last Updated](https://img.shields.io/github/last-commit/cdcgov/shareit-act/main?style=for-the-badge)](https://github.com/CDCgov/ShareIT-Act/actions/workflows/create-code-json.yml)

# Overview

The intention of this repository is to gather code repository metadata from various code environments produced by federal employees and contractors to comply with [H.R.9566 - SHARE IT Act](https://www.congress.gov/bill/118th-congress/house-bill/9566) for [Centers for Disease Control and Prevention (CDC)](https://www.cdc.gov) with the intention to share code with other federal agencies and general public.

[Centers for Disease Control and Prevention (CDC)](https://www.cdc.gov) is an [operating division (OpDiv)](https://www.hhs.gov/about/agencies/hhs-agencies-and-offices/index.html) of [Department of Health and Human Services (HHS)](https://www.hhs.gov/).

To adhere to [H.R.9566 - SHARE IT Act](https://www.congress.gov/bill/118th-congress/house-bill/9566), we produce a [code.json](./data/code.json) file in accordance to [HHS's code.json](https://www.hhs.gov/code.json) to eventually follow [Centers for Medicare & Medicaid Services (CMS)](https://github.com/DSACMS/gov-codejson/blob/main/docs/metadata.md)'s schema.

## Important Dates

The publication dates are set in accordance to our interpretation of [H.R.9566 - SHARE IT Act](https://www.congress.gov/bill/118th-congress/house-bill/9566).

| Year | Review Period             | Publishing Date |
| ---- | ------------------------- | --------------- |
| 2025 | Jun 06 2025 – Jul 18 2025 | Jul 21 2025     |
| 2025 | Nov 16 2025 – Dec 28 2025 | Dec 31 2025     |
| 2026 | Jun 06 2026 – Jul 18 2026 | Jul 21 2026     |
| 2026 | Nov 16 2026 – Dec 28 2026 | Dec 31 2026     |

## Internal Review

We expect project teams and internal [Centers, Institutes, and Offices (CIOs)](https://www.cdc.gov/about/organization/index.html) to review the provided [code.json](data/code.json) information for accuracy.

- Review repository metadata.
- Confirm accuracy of key fields (e.g., `Org`, `Contact Email`, `Exemption`, etc.).
- Submit corrections through pull requests for the current preview
- Ensure long-term compliance by updating `README.md` files to persist changes

## Review Metadata

To ease the reviewing of metadata, we provide a [CDC Metadata Browser](https://cdcgov.github.io/ShareIT-Act/index.html) to go through an existing code.json file.

1. Open the latest **[CDC Metadata Browser](https://cdcgov.github.io/ShareIT-Act/index.html)** file published in this repository.
2. Search by:
   - Repository name
   - Org or CDC program
   - Contact email
   - Exemption status
3. Review key fields, including:
   - `Repository Name`
   - `Organization`
   - `Contact Email`
   - `Exemption`
   - `Repository URL`
   - `Version`
   - `Status`

## Submitting Changes

There are two primary ways to ensure your metadata is accurate, depending on the type of change.

### 1. Update Your `README.md` (Recommended for Org, Email, & Exemptions)

This is the **most direct and permanent method** for correcting your **Organization**, **Contact Email**, or **Exemption** status. The automated scanner will use these markers to override incorrect values on the next scan.

1. In your repository, open the `README.md` file for editing.

2. Add one or more of the following markers in the file, each on its own line. Place them rather closer to the top of the file to facilitate the scanner processing these. Example:

   ```md
   Org: NCCDPHP
   Contact Email: chronicdev@cdc.gov
   Exemption: exemptByAgencySystem
   Exemption Justification: This code is used only within CDC infrastructure and is not reusable externally.
   ```

3. Commit this change to your repository's default branch.
   👉 For a complete list of available markers, please see the [CDC Metadata Implementation Guide](https://docs.cdc.gov/docs/ea/codeshare/implementation-guide#readmemd-override-optional-markers).

### 2. Use the Interactive Metadata Browser (For All Other Changes)

For changes to any other metadata field, you can suggest an update by creating a GitHub issue directly from the browser.

1. Open the **[CDC Metadata Browser](https://cdcgov.github.io/ShareIT-Act/index.html)**.

2. Search for your repository and click the **"Details"** button.

3. In the pop-up window, click **"Update Metadata via README"** to see instructions for the most common changes. For other changes, click **"Suggest Other Change via Issue"** (if enabled) to open a pre-filled GitHub issue.

4. Describe the changes you need and submit the issue for review.

## Partnership with Centers for Medicare and Medicaid Services (CMS)

We have an active partnership with the Centers for Medicare and Medicaid Services (CMS) to work towards [a common code.json framework](https://github.com/DSACMS/gov-codejson/blob/main/docs/metadata.md).

## Questions

Email [shareit@cdc.gov](mailto:shareit@cdc.gov?subject=Feedback) for help or clarification.
