# Design

This document tracks the architecture for `ex5`.

## Ownership

- Base and integration: `core/`
- Evolution AI: `evolution/`
- Networking: `network/`
- Tower attributes: `towers/`
- Combat and effects: `combat/`
- Versus mode and presentation: `presentation/`

## Runtime Modes

- `SoloGame`: local single-player fallback
- `HostGame`: authoritative server simulation
- `ClientGame`: rendering and input client
