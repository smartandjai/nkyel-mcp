{{/*
Common helpers for the nkyel chart.
*/}}

{{- define "nkyel.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "nkyel.fullname" -}}
{{- $name := default .Chart.Name .Values.nameOverride -}}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "nkyel.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "nkyel.labels" -}}
helm.sh/chart: {{ include "nkyel.chart" . }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}

{{- define "nkyel.selectorLabels" -}}
app.kubernetes.io/name: {{ include "nkyel.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}

{{- define "nkyel.namespace" -}}
{{- default .Release.Namespace .Values.namespace -}}
{{- end -}}

{{- define "nkyel.imagePullSecrets" -}}
{{- with .Values.image.pullSecrets }}
imagePullSecrets:
{{- toYaml . | nindent 0 }}
{{- end }}
{{- end -}}

{{/* Fully-qualified image refs for the three nkyel images.
     When `image.registry` is empty, omit the prefix so the ref is
     `nkyel-gateway:latest` (local-image mode, imagePullPolicy: Never). */}}
{{- define "nkyel.gatewayImage" -}}
{{- if .Values.image.registry -}}{{- printf "%s/%s:%s" .Values.image.registry .Values.image.gatewayImage .Values.image.tag -}}
{{- else -}}{{- printf "%s:%s" .Values.image.gatewayImage .Values.image.tag -}}{{- end -}}
{{- end -}}

{{- define "nkyel.frontendImage" -}}
{{- if .Values.image.registry -}}{{- printf "%s/%s:%s" .Values.image.registry .Values.image.frontendImage .Values.image.tag -}}
{{- else -}}{{- printf "%s:%s" .Values.image.frontendImage .Values.image.tag -}}{{- end -}}
{{- end -}}

{{- define "nkyel.provisionerImage" -}}
{{- if .Values.image.registry -}}{{- printf "%s/%s:%s" .Values.image.registry .Values.image.provisionerImage .Values.image.tag -}}
{{- else -}}{{- printf "%s:%s" .Values.image.provisionerImage .Values.image.tag -}}{{- end -}}
{{- end -}}

{{- define "nkyel.nginxImage" -}}
{{- printf "%s:%s" .Values.nginx.image.repository .Values.nginx.image.tag -}}
{{- end -}}

{{/* PVC name for the .nkyel home directory. */}}
{{- define "nkyel.homePVC" -}}
{{- printf "%s-home" (include "nkyel.fullname" .) -}}
{{- end -}}

{{/* Name of the Secret holding provider/channel keys. */}}
{{- define "nkyel.providerSecret" -}}
{{- if .Values.existingSecret -}}{{- .Values.existingSecret -}}
{{- else -}}{{- printf "%s-provider" (include "nkyel.fullname" .) -}}{{- end -}}
{{- end -}}

{{/* Name of the Secret holding the app secrets (BETTER_AUTH_SECRET,
     NKYEL_INTERNAL_AUTH_TOKEN, AUTH_JWT_SECRET, PROVISIONER_API_KEY,
     NKYEL_CREDENTIALS_KEY).
     `existingAppSecret` points every consumer (gateway, frontend,
     provisioner) at a user-managed Secret instead and skips generating one;
     it must carry PROVISIONER_API_KEY while the provisioner is enabled and
     AUTH_JWT_SECRET for more than one gateway instance. */}}
{{- define "nkyel.appSecret" -}}
{{- if .Values.existingAppSecret -}}{{- .Values.existingAppSecret -}}
{{- else -}}{{- printf "%s-app" (include "nkyel.fullname" .) -}}{{- end -}}
{{- end -}}

{{/* "true" when more than one gateway instance shares the database. An explicit
     boolean `gateway.multiInstance` wins -- set it before scaling with
     `kubectl scale` or an HPA, which change the replica count without a Helm
     upgrade -- otherwise it is derived from `gateway.replicas`. */}}
{{- define "nkyel.gatewayMultiInstance" -}}
{{- if kindIs "invalid" .Values.gateway.multiInstance -}}
{{- gt (int .Values.gateway.replicas) 1 -}}
{{- else -}}
{{- eq (toString .Values.gateway.multiInstance | lower) "true" -}}
{{- end -}}
{{- end -}}

{{/* PodDisruptionBudget minAvailable as Kubernetes accepts it: a positive
     integer or a percentage string such as "50%". Takes a dict with `value`
     (the raw values entry; unset falls back to 1) and `key` (the values path,
     named in the error). `int` on "50%" is 0 -- a budget that protects
     nothing -- so a YAML number renders as an integer, a digit string from
     --set-string becomes that integer, a percentage is preserved quoted, and
     0, "0%", more than 100% or anything else fails the render. Anything that
     is not a plain Go number is normalized with toString before the string
     branches: Helm 3.18.0 loads YAML numbers as json.Number, whose kind is
     "string" but which regexMatch and friends reject at argument validation,
     so the unoverridden default would otherwise fail every multi-replica
     render on that release. */}}
{{- define "nkyel.pdbMinAvailable" -}}
{{- $raw := .value -}}
{{- if kindIs "invalid" $raw -}}{{- $raw = 1 -}}{{- end -}}
{{- $hint := printf "%s must be a positive integer or a percentage such as \"50%%\" (got %v); a budget of 0 protects nothing, so set %s to false instead" .key $raw (replace ".minAvailable" ".enabled" .key) -}}
{{- if or (kindIs "float64" $raw) (kindIs "int64" $raw) (kindIs "int" $raw) -}}
{{- if or (lt (int $raw) 1) (ne (float64 (int $raw)) (float64 $raw)) -}}{{- fail $hint -}}{{- end -}}
{{- int $raw -}}
{{- else -}}
{{- $text := toString $raw -}}
{{- if regexMatch "^[0-9]+$" $text -}}
{{- if lt (atoi $text) 1 -}}{{- fail $hint -}}{{- end -}}
{{- atoi $text -}}
{{- else if regexMatch "^[0-9]+%$" $text -}}
{{- $percent := atoi (trimSuffix "%" $text) -}}
{{- if or (lt $percent 1) (gt $percent 100) -}}{{- fail $hint -}}{{- end -}}
{{- $text | quote -}}
{{- else -}}
{{- fail $hint -}}
{{- end -}}
{{- end -}}
{{- end -}}

{{/* Name of the postgres StatefulSet/Service. */}}
{{- define "nkyel.postgresFullname" -}}
{{- printf "%s-postgres" (include "nkyel.fullname" .) -}}
{{- end -}}

{{/* Name of the operator-managed postgres Secret, or empty when the chart owns
     the credentials. This is the only place the precedence chain is encoded:
     databaseUrlSecret, the gateway's DATABASE_URL, the StatefulSet's
     POSTGRES_PASSWORD and postgres-secret.yaml's render gate all read it, so a
     source added here cannot make them disagree.

     `default` rather than `or`: `or` returns its last operand even when falsy,
     so `existingSecret: false` (or `0`) would render the literal name
     "false". Chaining `default` keeps the old if/else-if truthiness and yields
     an empty string for any falsy value. */}}
{{- define "nkyel.databaseUserSecret" -}}
{{- .Values.postgresql.external.existingSecret | default .Values.postgresql.existingSecret | default "" -}}
{{- end -}}

{{/* Name of the Secret holding DATABASE_URL (and, in bundled mode, the
     postgres superuser password). Resolution order:
       1. postgresql.external.existingSecret (user-managed, key=database-url)
       2. postgresql.existingSecret          (user-managed, bundled image)
       3. chart-managed secret `<release>-postgres`
     Only #3 is created by this chart; #1/#2 must exist already. */}}
{{- define "nkyel.databaseUrlSecret" -}}
{{- include "nkyel.databaseUserSecret" . | default (include "nkyel.postgresFullname" .) -}}
{{- end -}}

{{/* Name of the redis StatefulSet/Service. */}}
{{- define "nkyel.redisFullname" -}}
{{- printf "%s-redis" (include "nkyel.fullname" .) -}}
{{- end -}}

{{/* Name of the Secret holding the redis stream-bridge URL (key `redis-url`,
     plus `redis-password` in bundled mode when a password is set). Resolution:
       1. redis.external.existingSecret (user-managed, key=redis-url)
       2. redis.existingSecret          (user-managed, bundled image)
       3. chart-managed secret `<release>-redis`
     Only #3 is created by this chart; #1/#2 must exist already. */}}
{{- define "nkyel.redisUrlSecret" -}}
{{- include "nkyel.redisUserSecret" . | default (include "nkyel.redisFullname" .) -}}
{{- end -}}

{{/* Name of the operator-managed redis Secret, or empty when the chart owns the
     credentials. Only the chart-managed Secret is created by this chart, and
     only there is the AUTH password known at render time — a user-managed
     Secret may or may not carry `redis-password`.

     Same truthiness rule as databaseUserSecret: `default` (not `or`) so a
     falsy `existingSecret` yields an empty string instead of the literal name
     "false". */}}
{{- define "nkyel.redisUserSecret" -}}
{{- .Values.redis.external.existingSecret | default .Values.redis.existingSecret | default "" -}}
{{- end -}}

{{/* Args for the bundled redis container. With a user-managed Secret the
     password is only knowable at runtime, so the container reads
     `redis-password` from that Secret and enables AUTH only when the value is
     nonempty. This keeps a `redis-url`-only Secret in no-auth mode instead of
     failing to start, and keeps a stale `redis.auth.password` from winning over
     the user-managed Secret (values.yaml documents it as ignored there). */}}
{{- define "nkyel.redisServerArgs" -}}
{{- if include "nkyel.redisUserSecret" . -}}
if [ -n "$REDIS_PASSWORD" ]; then exec redis-server --appendonly yes --requirepass "$REDIS_PASSWORD"; fi; exec redis-server --appendonly yes
{{- else if .Values.redis.auth.password -}}
exec redis-server --appendonly yes --requirepass "$REDIS_PASSWORD"
{{- else -}}
exec redis-server --appendonly yes
{{- end -}}
{{- end -}}

{{/* Readiness/liveness command for the bundled redis container. Mirrors
     redisServerArgs so the probes authenticate exactly when the server has a
     password — otherwise a password-protected server reports itself unhealthy. */}}
{{- define "nkyel.redisPingCommand" -}}
{{- if include "nkyel.redisUserSecret" . -}}
if [ -n "$REDIS_PASSWORD" ]; then redis-cli --no-auth-warning -a "$REDIS_PASSWORD" ping; else redis-cli ping; fi
{{- else if .Values.redis.auth.password -}}
redis-cli --no-auth-warning -a "$REDIS_PASSWORD" ping
{{- else -}}
redis-cli ping
{{- end -}}
{{- end -}}

{{/* Whether any redis stream-bridge backend is configured (bundled StatefulSet,
     external URL, or a user-managed Secret). Drives the env injection in the
     gateway deployment. */}}
{{- define "nkyel.redisConfigured" -}}
{{- or .Values.redis.enabled .Values.redis.external.redisUrl (include "nkyel.redisUserSecret" .) -}}
{{- end -}}

{{/* SHA256 checksums of the ConfigMaps. Mount these as pod-template
     annotations: ConfigMaps mounted via subPath do NOT receive live updates,
     so a `helm upgrade` that only changes a ConfigMap would leave pods on stale
     config. A checksum annotation makes any content change alter the pod spec,
     which triggers a rolling restart. */}}
{{- define "nkyel.configChecksum" -}}
{{- include (print $.Template.BasePath "/configmap-config.yaml") . | sha256sum -}}
{{- end -}}

{{- define "nkyel.extensionsChecksum" -}}
{{- include (print $.Template.BasePath "/configmap-extensions.yaml") . | sha256sum -}}
{{- end -}}

{{- define "nkyel.nginxChecksum" -}}
{{- include (print $.Template.BasePath "/configmap-nginx.yaml") . | sha256sum -}}
{{- end -}}

{{/* Percent-encode a string for safe interpolation into a URL userinfo
     (password) segment of a DSN. Sprig lacks urlqueryescape, and
     regexReplaceAllLiteral treats `replacement` as a regex template so chars
     like `[`, `]`, `?` break it - so we chain plain `replace` calls instead.
     `%` is encoded first to avoid double-encoding the percent signs emitted
     for the other characters. Covers the URL-special chars a managed-DB
     password might contain (`@ : / # ? % [ ]` and space). */}}
{{- define "nkyel.urlEscape" -}}
{{- $s := . -}}
{{- $s = replace "%" "%25" $s -}}
{{- $s = replace "@" "%40" $s -}}
{{- $s = replace ":" "%3A" $s -}}
{{- $s = replace "/" "%2F" $s -}}
{{- $s = replace "#" "%23" $s -}}
{{- $s = replace "?" "%3F" $s -}}
{{- $s = replace "[" "%5B" $s -}}
{{- $s = replace "]" "%5D" $s -}}
{{- $s = replace " " "%20" $s -}}
{{- $s -}}
{{- end -}}
