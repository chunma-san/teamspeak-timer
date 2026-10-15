<!-- typing-title:start -->
<p align="center">
  <a href="https://github.com/DenverCoder1/readme-typing-svg">
    <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&amp;weight=600&amp;size=28&amp;duration=3500&amp;pause=1800&amp;color=EF4444&amp;center=true&amp;vCenter=true&amp;width=760&amp;height=65&amp;repeat=true&amp;lines=Great+Love+Immortal+Venerable;Heaven+Refining+Demon+Venerable" alt="Great Love Immortal Venerable / Heaven Refining Demon Venerable" />
  </a>
</p>
<!-- typing-title:end -->

<!-- discord-presence:start -->
<p align="center">
  <a href="https://discord.com/users/891081797318897715">
    <img src="https://lanyard.cnrad.dev/api/891081797318897715?theme=dark&amp;bg=100b0d&amp;borderRadius=16px&amp;showDisplayName=true&amp;animated=true&amp;animatedDecoration=true" alt="Discord profile and live activity" />
  </a>
</p>
<!-- discord-presence:end -->

![TeamSpeak Timer: animated project banner](assets/banner.svg)

<!-- project-navigation:start -->
<p align="center"><a href="https://github.com/chunma-san">Profile &amp; projects</a> · <a href="#quick-start">Quick start</a> · <a href="https://github.com/chunma-san/teamspeak-timer/issues">Issues</a></p>
<!-- project-navigation:end -->

# TeamSpeak Timer

A configurable voice announcement timer that sends playback requests to TS3AudioBot API endpoints.

**Runtime:** Python 3.11+ · **Configuration:** environment variables · **Deployment:** self-hosted

## Quick start

The supported deployment target is Linux. Create an isolated Python environment:

```sh
python3 -m venv venv
. venv/bin/activate
# This script uses the Python standard library.
cp .env.example .env
# Edit .env first. Use shell-compatible quoting for JSON and values with spaces.
set -a
. ./.env
set +a
python timer.py
```

Only source a configuration file you created and trust. Starting the application can connect to external services; configure credentials and destinations first.

## Usage

Set TS_BOTS to a JSON array such as `[{"url":"http://127.0.0.1:58913/api/bot/use/0","token_env":"AUDIOBOT_TOKEN"}]`. Store that endpoint's authentication value in AUDIOBOT_TOKEN. Set AUDIO_ACTIVE, AUDIO_WARN40, AUDIO_WARN20, AUDIO_ZEAL and AUDIO_SPAM to audio paths visible to the audio bots. Review the timing constants before use.

## Configuration

`.env.example` contains placeholders only. Real credentials, IDs, storage locations and account settings belong in your private local configuration.

| Variable | Requirement |
| --- | --- |
| `AUDIOBOT_TOKEN` | TS3AudioBot API authentication value; keep it secret. |
| `AUDIO_ACTIVE` | Audio path for the active announcement, accessible to each audio bot. |
| `AUDIO_SPAM` | Audio path for the spam announcement, accessible to each audio bot. |
| `AUDIO_WARN20` | Audio path for the warn20 announcement, accessible to each audio bot. |
| `AUDIO_WARN40` | Audio path for the warn40 announcement, accessible to each audio bot. |
| `AUDIO_ZEAL` | Audio path for the zeal announcement, accessible to each audio bot. |
| `TS_BOTS` | JSON array of API URLs and token environment-variable names. |

## How it works and operational notes

Requires curl and separately installed TS3AudioBot instances. This repository contains the controller, not the audio-bot implementation or audio recordings. Create `/run/teamspeak-ts-timer` with ownership assigned to the timer service user before startup. The process creates and reads the `control` FIFO there. Authorized local processes can send `start`, `stop`, `status` or `quit` lines through that FIFO.

## Project layout

- Source files implement the application and integrations.
- `requirements.txt` or the project file declares dependencies.
- `.env.example` documents configuration names without live values.
- `.gitignore` excludes credentials, sessions, generated data and build output.
- `assets/banner.svg` is an original animated vector illustration. It has a static fallback and respects reduced-motion preferences in supporting viewers.

## Verification

See [VALIDATION.md](VALIDATION.md) for the checks performed on this publication snapshot and the remaining deployment checks. A source check is not an end-to-end test of Discord, Telegram, music sites or your host.

## Privacy and upstream services

This repository is a configurable source distribution. It does not include a production database, personal saved-link collection, message archive, credentials, media library or existing Git history. Review local changes before committing them.

Third-party APIs, libraries and products remain the work of their respective maintainers. Review their terms and licenses before redistribution or deployment. The original project artwork is stored locally; it does not depend on a remote GIF or tracking service.
