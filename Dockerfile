# syntax=docker/dockerfile:1
FROM node:24-bookworm-slim AS base
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends openssl ca-certificates && rm -rf /var/lib/apt/lists/*
ENV NEXT_TELEMETRY_DISABLED=1
FROM base AS build
COPY . .
RUN --mount=type=secret,id=proxy_ca NODE_EXTRA_CA_CERTS=/run/secrets/proxy_ca npm ci     && npx prisma generate && npm run build && node docker/collect-notices.mjs && npm cache clean --force
FROM build AS migrate
USER node
CMD ["node", "docker/migrate.mjs"]
FROM base AS runtime
ENV NODE_ENV=production HOSTNAME=0.0.0.0 PORT=3000
COPY --from=build --chown=node:node /app/.next/standalone ./
COPY --from=build --chown=node:node /app/.next/static ./.next/static
COPY --from=build /app/third-party-notices ./third-party-notices
COPY --from=build /app/prisma ./prisma
COPY --from=build /app/docker ./docker
COPY --from=build /app/LICENSE /app/COPYRIGHT ./
USER node
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s CMD node docker/health.mjs
CMD ["node", "docker/start.mjs"]
