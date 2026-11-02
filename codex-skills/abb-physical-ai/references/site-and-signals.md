# Reported site and signal contracts

Reported target: Windows host / VMware Win7 x86 / TwinCAT 2.11 / CX9020-0111 /
EL6631 / ABB IRC5 / IRB6700-200/2.6 / RW 6.16 / RobotStudio 2025.3.
These are source-document facts until independently observed. Reported 616-1 PC
Interface is separate from RobotStudio Premium, SDK version, credentials and permissions.

| Meaning | PLC symbol candidate | PROFINET / ABB candidate |
|---|---|---|
| Start | `Array6_Plc_to_Robot[3]` | Output0[3], `diPN_Test`, Mapping 3 |
| Done (read-only) | `Array1_Robot_to_Plc[3]` | Input1[1], `doPN_Test`, Mapping 9 |
| Independent Stop | unknown | unknown; do not allocate Mapping 4 by assumption |

The new bridge accepts only the two named aliases, configured with exact confirmed
ADS symbol spelling and BOOL metadata. It has no variable write API.
ADS declaration lookup uses a vendor service named ReadWrite; this service sends
the symbol name and reads metadata, not a PLC control value write.

Start FALSE is not Stop. In the historical J6 contract clearing Start initiates a
return movement. In a verified cube handshake it may acknowledge completion.
Never apply one contract to the other. A stale Done=TRUE is not a new completion.

A Start bit only releases whichever code is already waiting on that DI. Module
upload/load, PP selection, RAPID running and reaching the correct wait are distinct.
The current inventory adapter returns module metadata, not RAPID source text/hashes.
It cannot prove the wait contract. Obtain explicit exported source for review;
do not claim inventory alone proves the cube routine is loaded.

TC2 PLC Runtime ports are 801/811/821/831. Select using observed site evidence;
do not substitute TC3 port 851. TSM XML is file configuration, never proof of active
Runtime or end-to-end PROFINET propagation.
