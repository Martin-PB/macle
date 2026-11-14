---------------- MODULE CaptureLifecycle ----------------
EXTENDS Naturals, TLC

(*
  Abstract lifecycle model for the Chrome MV3 Google Meet capture path.

  This model intentionally abstracts browser APIs. It does not claim that
  Chrome, MediaRecorder, OPFS, or the download manager implement these
  transitions correctly; those assumptions must be checked by adapter tests.
*)

VARIABLES
  phase,
  authorized,
  tabOpen,
  offscreen,
  stream,
  streamUseCount,
  recorder,
  stopRequested,
  mediaFinalized,
  manifestFinalized,
  mediaDownload,
  manifestDownload

vars ==
  << phase, authorized, tabOpen, offscreen, stream, streamUseCount,
     recorder, stopRequested, mediaFinalized, manifestFinalized,
     mediaDownload, manifestDownload >>

Phases ==
  {"Idle", "Preparing", "Recording", "Finalizing", "Saved", "Failed"}

OffscreenStates == {"Absent", "Loading", "Ready"}
StreamStates == {"None", "Fresh", "Consumed", "Expired"}
RecorderStates == {"Inactive", "Recording", "Stopped"}
DownloadStates == {"NotStarted", "InProgress", "Complete", "Interrupted"}

Init ==
  /\ phase = "Idle"
  /\ authorized = FALSE
  /\ tabOpen = TRUE
  /\ offscreen = "Absent"
  /\ stream = "None"
  /\ streamUseCount = 0
  /\ recorder = "Inactive"
  /\ stopRequested = FALSE
  /\ mediaFinalized = FALSE
  /\ manifestFinalized = FALSE
  /\ mediaDownload = "NotStarted"
  /\ manifestDownload = "NotStarted"

Attest ==
  /\ phase = "Idle"
  /\ authorized = FALSE
  /\ authorized' = TRUE
  /\ UNCHANGED <<tabOpen, offscreen, stream, streamUseCount, recorder,
                  stopRequested, mediaFinalized, manifestFinalized,
                  mediaDownload, manifestDownload, phase>>

RequestStart ==
  /\ phase = "Idle"
  /\ authorized
  /\ tabOpen
  /\ phase' = "Preparing"
  /\ UNCHANGED <<authorized, tabOpen, offscreen, stream, streamUseCount,
                  recorder, stopRequested, mediaFinalized, manifestFinalized,
                  mediaDownload, manifestDownload>>

CreateOffscreen ==
  /\ phase = "Preparing"
  /\ offscreen = "Absent"
  /\ offscreen' = "Loading"
  /\ UNCHANGED <<phase, authorized, tabOpen, stream, streamUseCount,
                  recorder, stopRequested, mediaFinalized, manifestFinalized,
                  mediaDownload, manifestDownload>>

OffscreenReady ==
  /\ phase = "Preparing"
  /\ offscreen = "Loading"
  /\ offscreen' = "Ready"
  /\ UNCHANGED <<phase, authorized, tabOpen, stream, streamUseCount,
                  recorder, stopRequested, mediaFinalized, manifestFinalized,
                  mediaDownload, manifestDownload>>

IssueStream ==
  /\ phase = "Preparing"
  /\ offscreen = "Ready"
  /\ tabOpen
  /\ stream = "None"
  /\ stream' = "Fresh"
  /\ UNCHANGED <<phase, authorized, tabOpen, offscreen, streamUseCount,
                  recorder, stopRequested, mediaFinalized, manifestFinalized,
                  mediaDownload, manifestDownload>>

ExpireStream ==
  /\ phase = "Preparing"
  /\ stream = "Fresh"
  /\ stream' = "Expired"
  /\ UNCHANGED <<phase, authorized, tabOpen, offscreen, streamUseCount,
                  recorder, stopRequested, mediaFinalized, manifestFinalized,
                  mediaDownload, manifestDownload>>

StartRecorder ==
  /\ phase = "Preparing"
  /\ authorized
  /\ tabOpen
  /\ offscreen = "Ready"
  /\ stream = "Fresh"
  /\ streamUseCount = 0
  /\ phase' = "Recording"
  /\ stream' = "Consumed"
  /\ streamUseCount' = streamUseCount + 1
  /\ recorder' = "Recording"
  /\ UNCHANGED <<authorized, tabOpen, offscreen, stopRequested,
                  mediaFinalized, manifestFinalized, mediaDownload,
                  manifestDownload>>

StartFailure ==
  /\ phase = "Preparing"
  /\ (tabOpen = FALSE \/ stream = "Expired")
  /\ phase' = "Failed"
  /\ recorder' = "Inactive"
  /\ UNCHANGED <<authorized, tabOpen, offscreen, stream, streamUseCount,
                  stopRequested, mediaFinalized, manifestFinalized,
                  mediaDownload, manifestDownload>>

RequestStop ==
  /\ phase = "Recording"
  /\ phase' = "Finalizing"
  /\ stopRequested' = TRUE
  /\ UNCHANGED <<authorized, tabOpen, offscreen, stream, streamUseCount,
                  recorder, mediaFinalized, manifestFinalized,
                  mediaDownload, manifestDownload>>

TabClosedOrNavigated ==
  /\ tabOpen
  /\ tabOpen' = FALSE
  /\ IF phase = "Recording"
        THEN /\ phase' = "Finalizing"
             /\ stopRequested' = TRUE
        ELSE IF phase = "Preparing"
               THEN /\ phase' = "Failed"
                    /\ stopRequested' = TRUE
               ELSE UNCHANGED <<phase, stopRequested>>
  /\ UNCHANGED <<authorized, offscreen, stream, streamUseCount, recorder,
                  mediaFinalized, manifestFinalized, mediaDownload,
                  manifestDownload>>

RecorderStopped ==
  /\ phase = "Finalizing"
  /\ recorder = "Recording"
  /\ recorder' = "Stopped"
  /\ UNCHANGED <<phase, authorized, tabOpen, offscreen, stream,
                  streamUseCount, stopRequested, mediaFinalized,
                  manifestFinalized, mediaDownload, manifestDownload>>

FinalizeMedia ==
  /\ phase = "Finalizing"
  /\ recorder = "Stopped"
  /\ ~mediaFinalized
  /\ mediaFinalized' = TRUE
  /\ UNCHANGED <<phase, authorized, tabOpen, offscreen, stream,
                  streamUseCount, recorder, stopRequested,
                  manifestFinalized, mediaDownload, manifestDownload>>

FinalizeManifest ==
  /\ phase = "Finalizing"
  /\ mediaFinalized
  /\ ~manifestFinalized
  /\ manifestFinalized' = TRUE
  /\ UNCHANGED <<phase, authorized, tabOpen, offscreen, stream,
                  streamUseCount, recorder, stopRequested,
                  mediaFinalized, mediaDownload, manifestDownload>>

BeginMediaDownload ==
  /\ phase = "Finalizing"
  /\ mediaFinalized
  /\ mediaDownload = "NotStarted"
  /\ mediaDownload' = "InProgress"
  /\ UNCHANGED <<phase, authorized, tabOpen, offscreen, stream,
                  streamUseCount, recorder, stopRequested,
                  mediaFinalized, manifestFinalized, manifestDownload>>

CompleteMediaDownload ==
  /\ phase = "Finalizing"
  /\ mediaDownload = "InProgress"
  /\ mediaDownload' = "Complete"
  /\ UNCHANGED <<phase, authorized, tabOpen, offscreen, stream,
                  streamUseCount, recorder, stopRequested,
                  mediaFinalized, manifestFinalized, manifestDownload>>

InterruptMediaDownload ==
  /\ phase = "Finalizing"
  /\ mediaDownload = "InProgress"
  /\ mediaDownload' = "Interrupted"
  /\ phase' = "Failed"
  /\ UNCHANGED <<authorized, tabOpen, offscreen, stream, streamUseCount,
                  recorder, stopRequested, mediaFinalized,
                  manifestFinalized, manifestDownload>>

BeginManifestDownload ==
  /\ phase = "Finalizing"
  /\ manifestFinalized
  /\ manifestDownload = "NotStarted"
  /\ manifestDownload' = "InProgress"
  /\ UNCHANGED <<phase, authorized, tabOpen, offscreen, stream,
                  streamUseCount, recorder, stopRequested,
                  mediaFinalized, manifestFinalized, mediaDownload>>

CompleteManifestDownload ==
  /\ phase = "Finalizing"
  /\ manifestDownload = "InProgress"
  /\ manifestDownload' = "Complete"
  /\ UNCHANGED <<phase, authorized, tabOpen, offscreen, stream,
                  streamUseCount, recorder, stopRequested,
                  mediaFinalized, manifestFinalized, mediaDownload>>

InterruptManifestDownload ==
  /\ phase = "Finalizing"
  /\ manifestDownload = "InProgress"
  /\ manifestDownload' = "Interrupted"
  /\ phase' = "Failed"
  /\ UNCHANGED <<authorized, tabOpen, offscreen, stream, streamUseCount,
                  recorder, stopRequested, mediaFinalized,
                  manifestFinalized, mediaDownload>>

CompleteSession ==
  /\ phase = "Finalizing"
  /\ mediaFinalized
  /\ manifestFinalized
  /\ mediaDownload = "Complete"
  /\ manifestDownload = "Complete"
  /\ phase' = "Saved"
  /\ UNCHANGED <<authorized, tabOpen, offscreen, stream, streamUseCount,
                  recorder, stopRequested, mediaFinalized,
                  manifestFinalized, mediaDownload, manifestDownload>>

BrowserRestart ==
  /\ phase \in {"Preparing", "Recording", "Finalizing"}
  /\ phase' = "Failed"
  /\ offscreen' = "Absent"
  /\ stream' = "Expired"
  /\ recorder' = "Stopped"
  /\ stopRequested' = TRUE
  /\ UNCHANGED <<authorized, tabOpen, streamUseCount, mediaFinalized,
                  manifestFinalized, mediaDownload, manifestDownload>>

Next ==
  \/ Attest
  \/ RequestStart
  \/ CreateOffscreen
  \/ OffscreenReady
  \/ IssueStream
  \/ ExpireStream
  \/ StartRecorder
  \/ StartFailure
  \/ RequestStop
  \/ TabClosedOrNavigated
  \/ RecorderStopped
  \/ FinalizeMedia
  \/ FinalizeManifest
  \/ BeginMediaDownload
  \/ CompleteMediaDownload
  \/ InterruptMediaDownload
  \/ BeginManifestDownload
  \/ CompleteManifestDownload
  \/ InterruptManifestDownload
  \/ CompleteSession
  \/ BrowserRestart

TypeOK ==
  /\ phase \in Phases
  /\ authorized \in BOOLEAN
  /\ tabOpen \in BOOLEAN
  /\ offscreen \in OffscreenStates
  /\ stream \in StreamStates
  /\ streamUseCount \in 0..1
  /\ recorder \in RecorderStates
  /\ stopRequested \in BOOLEAN
  /\ mediaFinalized \in BOOLEAN
  /\ manifestFinalized \in BOOLEAN
  /\ mediaDownload \in DownloadStates
  /\ manifestDownload \in DownloadStates

AuthorizationSafety ==
  phase \in {"Preparing", "Recording", "Finalizing", "Saved"} => authorized

RecorderRequiresReadyOffscreen ==
  recorder = "Recording" => offscreen = "Ready"

RecorderRequiresConsumedStream ==
  recorder = "Recording" => stream = "Consumed" /\ streamUseCount = 1

SavedMeansBothDownloadsComplete ==
  phase = "Saved" =>
    /\ mediaFinalized
    /\ manifestFinalized
    /\ mediaDownload = "Complete"
    /\ manifestDownload = "Complete"

DownloadRequiresFinalizedArtifact ==
  /\ (mediaDownload \in {"InProgress", "Complete"} => mediaFinalized)
  /\ (manifestDownload \in {"InProgress", "Complete"} => manifestFinalized)

RecordingPhaseConsistency ==
  phase = "Recording" => recorder = "Recording"

StopEventuallyTerminates ==
  stopRequested ~> (phase = "Saved" \/ phase = "Failed")

Spec ==
  Init
  /\ [][Next]_vars
  /\ WF_vars(RecorderStopped)
  /\ WF_vars(FinalizeMedia)
  /\ WF_vars(FinalizeManifest)
  /\ WF_vars(BeginMediaDownload)
  /\ WF_vars(CompleteMediaDownload)
  /\ WF_vars(BeginManifestDownload)
  /\ WF_vars(CompleteManifestDownload)
  /\ WF_vars(CompleteSession)

=============================================================
