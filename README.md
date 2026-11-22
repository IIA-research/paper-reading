# Interactive Intent Alignment (IIA) Paper Reading

Site: https://iia-research.github.io/paper-reading/

Each of us owns a section of the Interactive Intent Alignment literature and writes up our take on every paper in it. Everyone else reads, comments and discusses underneath.

## Writing a note

1. Open a paper on the site.
2. Under **Notes**, enter your GitHub username and a nickname once (your browser remembers both) and click **Write a note**.
3. GitHub opens a new-file page named `your-username.md` with a starter template. Write in Markdown; math works with `$...$` and `$$...$$`.

The file name is your GitHub username, which links the note to your account (avatar, Edit, History). The nickname is what readers see, set in the front matter at the top of the note:

```markdown
---
name: "Your nickname"
---
```

Your newest note's nickname is shown on all your notes, so to change it, edit it in any one note. A note without a nickname shows the GitHub username.
4. Click **Commit changes**. The site updates within a minute or two.

To change your note later, click **Edit** on it.

Notes live at `notes/<paper id>/<github username>.md` — one file per person per paper, so nobody overwrites anyone else. Raw HTML is not rendered.

## Recommended papers (admins)

`featured.yaml` lists the papers the organizers recommend reading first. They are listed, in file order, on the Recommended page, carry a ★ Recommended mark in the list and on the paper page, and can be filtered or sorted first. To recommend a paper, add its id; `why` (a line for newcomers) and `by` are optional:

```yaml
- id: "2610.12655"
  why: Clear formulation of when asking is worth it.
  by: your-github-username
```

## Figures and thumbnails

When a paper gets its first note, the deploy workflow downloads that paper's PDF from arXiv, crops its Figure 1 to `figs/` and saves a small image of page 1 to `thumbs/` (used when there is no Figure 1), then commits them. Only noted papers get them. If a crop looks wrong, replace `figs/<paper id>.webp` with your own image; it is never regenerated. To make them locally: `python scripts/make_thumbs.py`.

## Commenting

The bottom of every paper page is a comment thread. Sign in with GitHub to comment or reply. Comments are stored in this repository's [Discussions](https://github.com/IIA-research/paper-reading/discussions), so you can also reply there.

## Sections and papers

- **Sections and owners**: `sections` in `site.yaml`; put owners' GitHub usernames under `owners`.
- **Papers**: `papers.yaml`, one entry per paper. Don't change `id` — note folders and comment threads are keyed on it. `section` must match a section `key` in `site.yaml`.
- The initial list was imported from the IIA literature map (out-of-scope papers skipped) with `scripts/import_iia.py`.

## Local preview

```bash
pip install -r requirements.txt
python build.py
python -m http.server -d _site 8000
```

Then open http://localhost:8000.

## One-time setup (admins)

1. **Settings → Pages → Source**: choose **GitHub Actions**. Every push to `main` then redeploys the site.
2. **Settings → General → Features**: enable **Discussions**, and create a `Paper discussions` category with the **Announcement** format.
3. Install the [giscus app](https://github.com/apps/giscus) on the org for this repository only, then copy `repo_id` and `category_id` from https://giscus.app into `giscus` in `site.yaml`.
