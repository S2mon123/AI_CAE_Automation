# RobotStudio 2025.3 API Audit

This file records only APIs verified in the locally installed `25.3.11371.0` assemblies. It avoids relying on renamed RobotStudio 2026.1 types such as `VirtualController`; 2025.3 uses `RsIrc5Controller` and `Station.Irc5Controllers`.

## Station SDK signatures used

- `Station.ActiveStation`, `Station.GetAllObjects()`, `Station.ActiveTask`, `Station.Irc5Controllers`
- `RsTask.Targets`, `RsTask.PathProcedures`, `RsTask.DataDeclarations`
- `RsIrc5Controller.SystemId`, `.Tasks`, `.MechanicalUnits`
- `Mechanism.GetJointValues()`, `.GetJointLimits(out double[], out double[])`, `.GetJointTypes()`
- `RsToolData.Frame`, `RsWorkObject.UserFrame`, `RsWorkObject.ObjectFrame`
- `RsRobTarget.Frame`, `.ConfigurationData`, `.GetExternalAxes(bool)`
- `RsJointTarget.GetRobotAxes(bool)`, `.GetExternalAxes(bool)`
- `RsPathProcedure.Instructions`
- `RsMoveInstruction.GetToPointArgument()`, `.GetViaPointArgument()`, `.GetCirPointArgument()`, `.GetToolArgument()`, `.GetWObjArgument()`

## PC SDK signatures used

- `NetworkScanner.Scan()`, `NetworkScanner.Controllers`
- `Controller.Connect(ControllerInfo, ConnectionType.RobotStudio, bool)`
- `Controller.Logon(UserInfo.DefaultLocalUser)`, `Controller.Logoff()`, `Controller.Dispose()`
- `Controller.IsVirtual`, `.State`, `.OperatingMode`, `.RobotWareVersion`, `.Rapid`, `.EventLog`, `.IOSystem`
- `Rapid.GetTasks()`, `Rapid.ExecutionStatus`
- `Task.GetModules()`, `Task.ProgramPointer`, `Task.MotionPointer`
- `Module.GetRoutines()` and read-only metadata properties
- `EventLog.GetAllMessages(int, int)`, `EventLog.GetMessagesByCategory(int, int, int)`
- `IOSystem.GetSignals(IOFilterTypes.All)`, `IOSystem.GetSignal(string)`

## Official references

- [RobotStudio SDK Add-In creation](https://developercenter.robotstudio.com/api/robotstudio/articles/How-To/Add-Ins/Creating-a-RobotStudio-Add-In.html)
- [RobotStudio Add-In loading](https://developercenter.robotstudio.com/api/robotstudio/articles/Concepts/AddinConcept/LoadingAdd-In.html)
- [PC SDK controller access](https://developercenter.robotstudio.com/api/pcsdk/articles/Manual/Using-the-PC-SDK/Accessing-the-controller.html)
- [PC SDK EventLog API](https://developercenter.robotstudio.com/api/pcsdk/api/ABB.Robotics.Controllers.EventLogDomain.EventLog.html)
- [PC SDK RAPID module behavior](https://developercenter.robotstudio.com/api/pcsdk/articles/Manual/Using-the-PC-SDK/Rapid-domain/Working-with-RAPID-modules-and-programs.html)
- [RobotStudio path target retrieval](https://developercenter.robotstudio.com/api/robotstudio/articles/How-To/Targets-and-Paths/RetrieveRsTargets.html)

Module source export is not implemented in Phase 1 because `Module.SaveToFile` writes to the controller filesystem and local export requires an additional PC SDK file-transfer workflow. That write/evidence boundary belongs to Phase 3.
