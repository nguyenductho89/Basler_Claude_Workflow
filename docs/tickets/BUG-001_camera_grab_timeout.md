# BUG-001: Camera Grab Timeout on Software Trigger Mode

## Summary
Camera grab times out immediately after connection when configured with software trigger mode because no trigger signal is being sent.

## Priority
**High** - Blocks camera operation

## Status
Open

## Environment
- Camera: Basler acA4600-7gc (22039212)
- Configuration: exposure=50.0us, trigger=software

## Steps to Reproduce
1. Start the application
2. Connect to camera
3. Camera connects successfully but immediately shows grab timeout error

## Expected Behavior
Camera should either:
1. Automatically send software triggers when in software trigger mode, OR
2. Fall back to free-run mode for continuous acquisition

## Actual Behavior
```
2025-12-27 09:57:58 - src.services.camera_service - INFO - Camera configured: exposure=50.0us, trigger=software
2025-12-27 09:57:58 - src.services.camera_service - INFO - Connected to camera: Basler acA4600-7gc (22039212)
2025-12-27 09:57:58 - src.services.camera_service - INFO - Started grabbing
2025-12-27 09:57:59 - src.services.camera_service - ERROR - Error grabbing frame: Grab timed out.
Possible reasons are:
- The image transport from the camera device is not working properly
- The camera uses explicit triggering and has not been triggered
```

## Root Cause Analysis
The camera is configured with `trigger=software` mode, which means the camera waits for an explicit software trigger command (`camera.ExecuteSoftwareTrigger()`) before capturing each frame. However, the grab loop is not sending software triggers, causing the grab to timeout waiting for a trigger that never comes.

## Proposed Fix

### Option A: Add Software Trigger in Grab Loop (Recommended)
In `src/services/camera_service.py`, modify the grab loop to send software trigger when in software trigger mode:

```python
def _grab_frame(self):
    if self._camera is None:
        return None

    # Send software trigger if in software trigger mode
    if self._trigger_mode == "software":
        self._camera.ExecuteSoftwareTrigger.Execute()

    grab_result = self._camera.RetrieveResult(
        self._grab_timeout_ms,
        pylon.TimeoutHandling_ThrowException
    )
    # ... rest of grab logic
```

### Option B: Use Free-Run Mode for Continuous Acquisition
Change default trigger mode to "off" (free-run) for continuous frame acquisition without explicit triggering.

### Option C: External Trigger Integration
If software trigger is intended for PLC/IO synchronization, ensure the IO service sends trigger signals at the appropriate rate.

## Files to Modify
- `src/services/camera_service.py` - Add software trigger execution in grab loop
- `src/domain/config.py` - Consider changing default trigger mode

## Acceptance Criteria
- [ ] Camera grabs frames successfully in software trigger mode
- [ ] No grab timeout errors during normal operation
- [ ] Frame rate matches expected throughput
- [ ] All existing camera tests pass

## Related Documentation
- [Basler pylon Documentation - Software Trigger](https://docs.baslerweb.com/software-trigger)
- `src/services/camera_service.py:_grab_frame()`

## Created
2025-12-27

## Labels
`bug`, `camera`, `high-priority`, `blocking`
