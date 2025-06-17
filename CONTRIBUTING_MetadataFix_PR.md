# 🤝 How to Contribute Metadata Fixes via Pull Request

This guide explains how to submit metadata corrections to the CDC Share IT Act repository via GitHub Pull Request (PR). Anyone with a GitHub account can submit changes — no special access is required.

---

## ✅ What You Need
- A GitHub account
- A web browser (no local tools required)

---

## 🔁 Step 1: Fork the Repository

1. Visit: [https://github.com/CDCgov/ShareIT-Act](https://github.com/CDCgov/ShareIT-Act)
2. Click the **"Fork"** button in the top-right corner.
3. Select your GitHub account to create a copy of the repository.

---

## 📝 Step 2: Make Your Edits

- Navigate to the file you want to change, such as:
  - `code.json` – to correct metadata
  - `metadata_preview_table.html` – optional for readability
- Click the ✏️ **pencil icon** to edit.
- Make your changes, then scroll down and click **"Commit changes"** with a short description.

---

## 📤 Step 3: Submit a Pull Request (PR)

1. After committing, click the **“Compare & pull request”** button GitHub suggests.
2. Fill out the PR form:
   - **Title:** e.g., `Fix metadata for NCCDPHP repo`
   - **Description:** include:
     - Name of the affected repository
     - Explanation of the fix
     - Link to source if helpful
3. Click **"Create pull request"**.

💡 Tip: Mention `metadata-fix` in your PR to help reviewers triage faster.

---

## 🧠 Making Metadata Persistent

If you'd like your metadata fix to **persist across future scans**, also update your repository’s `README.md` file using override markers such as:

```md
Org: NCCDPHP
Contact Email: chronicdev@cdc.gov
Exemption: exemptByAgencySystem
Exemption Justification: This code is internal to CDC and not intended for reuse.
```

📘 [View override marker documentation](https://docs.cdc.gov/docs/ea/codeshare/implementation-guide#readmemd-override-optional-markers)

---

## 🔐 Permissions

You do **not** need write access to submit PRs. Your submission will be reviewed by the CDC EA/EDSO team and merged if approved.

---

## 🆘 Questions?

Email: [shareit@cdc.gov](mailto:shareit@cdc.gov?subject=Metadata%20Correction%20Help)
Always CC: `#ea@cdc.gov` if responding to a formal metadata correction request.
