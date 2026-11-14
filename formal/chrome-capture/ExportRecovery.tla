---------------- MODULE ExportRecovery ----------------
EXTENDS Naturals, TLC

(*
  Recovery contract for a finalized local OPFS recording whose browser
  downloads were interrupted. The retained Blob is integrity-checked before
  any missing export is retried. Previously completed exports are preserved.
*)

VARIABLES
  phase,
  artifactRetained,
  metadataPresent,
  artifactHashValid,
  hashVerified,
  mediaState,
  manifestState,
  captureStarted

vars ==
  << phase, artifactRetained, metadataPresent, artifactHashValid,
     hashVerified, mediaState, manifestState, captureStarted >>

Phases == {"Pending", "Verifying", "Exporting", "Blocked", "Recovered"}
ExportStates == {"Pending", "InProgress", "Complete", "Interrupted"}

Init ==
  /\ phase = "Pending"
  /\ artifactRetained = TRUE
  /\ metadataPresent = TRUE
  /\ artifactHashValid \in BOOLEAN
  /\ hashVerified = FALSE
  /\ mediaState \in {"Pending", "Complete", "Interrupted"}
  /\ manifestState \in {"Pending", "Complete", "Interrupted"}
  /\ captureStarted = FALSE

RequestRecovery ==
  /\ phase = "Pending"
  /\ artifactRetained
  /\ metadataPresent
  /\ phase' = "Verifying"
  /\ UNCHANGED <<artifactRetained, metadataPresent, artifactHashValid,
                  hashVerified, mediaState, manifestState, captureStarted>>

VerifyIntegrity ==
  /\ phase = "Verifying"
  /\ IF artifactHashValid
        THEN /\ phase' = "Exporting"
             /\ hashVerified' = TRUE
        ELSE /\ phase' = "Blocked"
             /\ hashVerified' = FALSE
  /\ UNCHANGED <<artifactRetained, metadataPresent, artifactHashValid,
                  mediaState, manifestState, captureStarted>>

BeginMediaDownload ==
  /\ phase = "Exporting"
  /\ hashVerified
  /\ artifactRetained
  /\ mediaState \in {"Pending", "Interrupted"}
  /\ mediaState' = "InProgress"
  /\ UNCHANGED <<phase, artifactRetained, metadataPresent,
                  artifactHashValid, hashVerified, manifestState, captureStarted>>

CompleteMediaDownload ==
  /\ phase = "Exporting"
  /\ mediaState = "InProgress"
  /\ mediaState' = "Complete"
  /\ UNCHANGED <<phase, artifactRetained, metadataPresent,
                  artifactHashValid, hashVerified, manifestState, captureStarted>>

InterruptMediaDownload ==
  /\ phase = "Exporting"
  /\ mediaState = "InProgress"
  /\ mediaState' = "Interrupted"
  /\ UNCHANGED <<phase, artifactRetained, metadataPresent,
                  artifactHashValid, hashVerified, manifestState, captureStarted>>

BeginManifestDownload ==
  /\ phase = "Exporting"
  /\ hashVerified
  /\ artifactRetained
  /\ manifestState \in {"Pending", "Interrupted"}
  /\ manifestState' = "InProgress"
  /\ UNCHANGED <<phase, artifactRetained, metadataPresent,
                  artifactHashValid, hashVerified, mediaState, captureStarted>>

CompleteManifestDownload ==
  /\ phase = "Exporting"
  /\ manifestState = "InProgress"
  /\ manifestState' = "Complete"
  /\ UNCHANGED <<phase, artifactRetained, metadataPresent,
                  artifactHashValid, hashVerified, mediaState, captureStarted>>

InterruptManifestDownload ==
  /\ phase = "Exporting"
  /\ manifestState = "InProgress"
  /\ manifestState' = "Interrupted"
  /\ UNCHANGED <<phase, artifactRetained, metadataPresent,
                  artifactHashValid, hashVerified, mediaState, captureStarted>>

Recover ==
  /\ phase = "Exporting"
  /\ hashVerified
  /\ mediaState = "Complete"
  /\ manifestState = "Complete"
  /\ artifactRetained
  /\ metadataPresent
  /\ phase' = "Recovered"
  /\ artifactRetained' = FALSE
  /\ metadataPresent' = FALSE
  /\ UNCHANGED <<artifactHashValid, hashVerified, mediaState, manifestState, captureStarted>>

BrowserRestart ==
  /\ phase \in {"Verifying", "Exporting"}
  /\ phase' = "Pending"
  /\ hashVerified' = FALSE
  /\ mediaState' = IF mediaState = "InProgress" THEN "Interrupted" ELSE mediaState
  /\ manifestState' = IF manifestState = "InProgress" THEN "Interrupted" ELSE manifestState
  /\ UNCHANGED <<artifactRetained, metadataPresent, artifactHashValid, captureStarted>>

AttemptNewCapture ==
  /\ phase = "Recovered"
  /\ ~captureStarted
  /\ captureStarted' = TRUE
  /\ UNCHANGED <<phase, artifactRetained, metadataPresent, artifactHashValid,
                  hashVerified, mediaState, manifestState>>

Next ==
  \/ RequestRecovery
  \/ VerifyIntegrity
  \/ BeginMediaDownload
  \/ CompleteMediaDownload
  \/ InterruptMediaDownload
  \/ BeginManifestDownload
  \/ CompleteManifestDownload
  \/ InterruptManifestDownload
  \/ Recover
  \/ BrowserRestart
  \/ AttemptNewCapture

TypeOK ==
  /\ phase \in Phases
  /\ artifactRetained \in BOOLEAN
  /\ metadataPresent \in BOOLEAN
  /\ artifactHashValid \in BOOLEAN
  /\ hashVerified \in BOOLEAN
  /\ mediaState \in ExportStates
  /\ manifestState \in ExportStates
  /\ captureStarted \in BOOLEAN

MetadataRequiresRetainedArtifact ==
  metadataPresent => artifactRetained

DownloadRequiresVerifiedArtifact ==
  (mediaState = "InProgress" \/ manifestState = "InProgress") =>
    (hashVerified /\ artifactRetained /\ metadataPresent)

ExportingRequiresVerifiedHash ==
  phase = "Exporting" => hashVerified

BlockedMeansNoFalseSuccess ==
  phase = "Blocked" =>
    /\ ~hashVerified
    /\ artifactRetained
    /\ metadataPresent
    /\ mediaState # "InProgress"
    /\ manifestState # "InProgress"

RecoveredMeansTruthfulSuccess ==
  phase = "Recovered" =>
    /\ hashVerified
    /\ mediaState = "Complete"
    /\ manifestState = "Complete"
    /\ ~artifactRetained
    /\ ~metadataPresent

OnlyRecoveryRemovesArtifact ==
  ~artifactRetained => phase = "Recovered"

OnlyRecoveryRemovesMetadata ==
  ~metadataPresent => phase = "Recovered"

PendingRecoveryBlocksNewCapture ==
  metadataPresent => ~captureStarted

Spec ==
  Init
  /\ [][Next]_vars

=============================================================
