# Clean architecture in typescript & my learnings

## Folder structure
```bash
├── entities
│   └── user.entity.ts
├── frameworks
│   └── in-memory-users.repository.ts
├── interfaces
│   └── users.repository.ts
├── main.ts
├── package.json
├── README.md
├── tsconfig.json
└── usecases
    └── create-user.usecase.ts
```

core business logic is in `entity` folder.

in `frameworks`, there is the implementation of `interfaces`

and in `main.ts` an instance of repossitory implementation is injected into `entity`

## Run TypeScript

there is 3 options:
- transpile to js and run js (is not prefered for development)
- use ts-node
  + `npx ts-node main.ts`
- use tsx
  + `npx tsx main.ts`
