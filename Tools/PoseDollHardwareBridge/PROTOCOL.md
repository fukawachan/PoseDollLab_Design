# PDH1 diagnostic wire format v1

This is a separate single-real-axis instrument protocol. It is not the production HW44 USB/cohort protocol and does not connect to the UE pose TCP port.

ESP32-S3 native USB Serial/JTAG carries COBS(payload + CRC32) followed by one zero byte. All integers are little endian. Decoded size is exactly 60 bytes; payload size field is 56, excluding the CRC. CRC32 is IEEE/zlib over the first 56 bytes (init FFFFFFFF, reflected polynomial EDB88320, final xor FFFFFFFF).

| Offset | Bytes | Meaning |
|---:|---:|---|
| 0 | 4 | ASCII PDH1 |
| 4 | 1 | Version 1 |
| 5 | 1 | Message type 1 |
| 6 | 2 | Payload length 56 |
| 8 | 8 | Device ID from read-only eFuse base MAC |
| 16 | 8 | Per-boot random session ID |
| 24 | 8 | Increasing sequence, starts at 1 |
| 32 | 8 | Sender monotonic microseconds at start of register reads |
| 40 | 4 | Elapsed register-read window in microseconds |
| 44 | 2 | Axis index 17 (elbow_l.flex, diagnostic assignment) |
| 46 | 2 | Count 0..16383 when flags=0; wire value 0 otherwise |
| 48 | 2 | AS5048A diagnostic/AGC register |
| 50 | 2 | Magnitude |
| 52 | 2 | Combined zero-position register value |
| 54 | 2 | Flags |
| 56 | 4 | CRC32 |

Flags: bit0 SPI I/O, bit1 parity, bit2 sensor EF, bit3 missing OCF or COF/CompLow/CompHigh, bit4 nonzero zero-register setting. Other flags are rejected. An invalid count becomes null in host JSON, never a valid zero reading.

Read window describes SPI register reads, not the exact internal ADC acquisition timestamp. Diagnostic/magnitude/angle registers are sequential, not a simultaneous full-body cohort.

The host rejects unsupported versions, malformed frames, impossible health combinations, CRC failures, wrong axis IDs, duplicate/backward sequence/time, and device/session changes without reconnect. Oversize encoded frames are discarded to the next delimiter. A recorded file is not overwritten. Transport exceptions preserve bytes and accepted records collected before the exception.

The host only converts counts to raw degrees for inspection and circular statistics. It does not apply mechanical zero, sign, filters, or UE FK. Firmware only issues reads (including read-to-clear); it never writes sensor OTP. Future full-body firmware needs separate identity, capabilities, epoch assembly, bus fault handling and physical calibration ownership.

Run unit tests from the repository root:
~~~
python -m unittest discover -s Tools/PoseDollHardwareBridge -p "test_*.py" -v
~~~
Tests use synthetic packets explicitly; they do not qualify physical hardware.
