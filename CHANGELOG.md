# Changelog

## [Unreleased]
- None

## [2.2.0] - 2026-07-10
## Added
- **DB:** FITS observation metadata is added to the database (Fast Acquisition 1-3 GHz)

## [2.1.16] - 2026-07-06
### Fixed
- Fixed Django time formats for `en` locale
- Fixed branch merge in release script
- **DB:** Fixed time zone for field `datetime_obs_utc` for raw observations (Fast Acquisition 1-3 GHz)

## [2.1.14] - 2026-07-05
### Changed
- Disabled Redis RDB snapshots for cache and broker

### Fixed
- Fixed Django user privileges validation
- Resolved an issue where Docker started before NAS mounts

## [2.1.12] - 2026-07-05
### Changed
- Configured DB tables display in Django administration panel

## [2.1.9] - 2026-07-05
### Fixed
- Fixed Django administration panel access

## [2.1.0] - 2026-07-03
### Added
- Integrated backend, message broker and cache infrastructure

### Changed
- project structure

## [2.0.0] - 2026-05-22
### Changed
- Major project structure update

## [1.2.0] - 2026-04-20
### Added
- Multiprocessing support for the `bin2fits-fast-1-3` application