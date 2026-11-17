# How to update this profile

Everything comes from **`profile.yaml`**. `README.md`, `assets/skills.svg` and `site/index.html` are generated; don't edit them by hand.

## Quick edit (browser)

1. Open `profile.yaml` on GitHub and click the pencil.
2. Change what you need: a new skill, a level, a certification you earned, a new role.
3. Commit to `main`. CI validates the file, regenerates the README and the site, and commits them back.

## Edit with a review (recommended for bigger changes)

```bash
git checkout -b update-profile
# edit profile.yaml
pip install -r requirements.txt
python scripts/build.py        # validates and regenerates
git commit -am "Add AZ-305" && git push -u origin update-profile
```

Open a PR. CI fails if `profile.yaml` breaks the schema or if you forgot to regenerate.

## Common changes

| I want to… | Edit in `profile.yaml` |
| --- | --- |
| Add a skill area | a new entry under `skills:` with `category`, `level` (1–5), `items`, `evidence` |
| Raise a level | the `level:` of that area |
| Record a certification | under `certifications:` set `status: earned` and add `year:` |
| Add a role | a new entry at the top of `experience:` |
| Change the headline | `person.headline` |

Levels: 5 expert (lead and teach it), 4 advanced, 3 proficient, 2 learning, 1 aware.

## Rules

- Keep client names out unless you have permission to publish them.
- Every skill area should have an `evidence` line: something you did, not an adjective.

## One-time setup

- **GitHub Pages:** Settings → Pages → Source: **GitHub Actions**. The site is published from `site/`.
- **Profile README:** if this repo is named `dalbarado/dalbarado`, GitHub shows `README.md` on your profile page.
