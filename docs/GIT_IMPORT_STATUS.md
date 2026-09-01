# Git import status

- Target repository: `asdadas1113/nikke-calc`
- Target branch: `crown-mast-engine`
- Intended path: `research/crown-mast-engine/`
- Branch was created from master commit `fb2fd9157aa14499daf6b9f185beb685d4393f90`.
- The cleaned local source tree is authoritative for this import.
- Bulk transfer was not completed from the chat runtime because the GitHub connector exposes text-file/Git-object writes rather than a local-directory upload primitive.

## First development change

The default 12-burst measured timeline remains unchanged. A new uniform timeline constructor can generate an arbitrary number of cycles from the first-cycle intra-burst offsets and a caller-supplied measured interval. Standard Crown/Mast rotation policies now continue their patterns beyond cycle 12, while custom rotations accept any contiguous cycle range starting at 1.

The constructor does not assert that live raid bursts are actually uniform; the interval is an input to be replaced with measured data.
