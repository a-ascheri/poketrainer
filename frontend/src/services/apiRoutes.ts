export const API_V1 = '/api/v1';

export const ADMIN = `${API_V1}/admin`;
export const TRAINER = `${API_V1}/game/trainer`;
export const GAME = `${API_V1}/game`;
export const USER = `${API_V1}/user`;
export const SYSTEM = `${API_V1}/system`;
export const POKEMON = `${API_V1}/pokemon`;

export const API_ROUTES = {
  admin: {
    users: `${ADMIN}/users`,
    internalAdmins: `${ADMIN}/internal/admins`,
    trainers: `${ADMIN}/trainers`,
  },
  trainer: {
    starterOptions: `${TRAINER}/starter/options`,
    starterSelect: `${TRAINER}/starter/select`,
    gainExperience: (trainerPokemonId: number) =>
      `${TRAINER}/pokemon/${trainerPokemonId}/gain-exp`,
    pokemonStats: (trainerPokemonId: number) => `${TRAINER}/pokemon/${trainerPokemonId}/stats`,
    pokemonMoves: (trainerPokemonId: number) => `${TRAINER}/pokemon/${trainerPokemonId}/moves`,
    pokemonList: `${TRAINER}/pokemon`,
  },
  user: {
    authorize: `${USER}/authorize`,
    token: `${USER}/token`,
    login: `${USER}/login`,
    register: `${USER}/register`,
    profile: `${USER}/profile`,
    changePassword: `${USER}/change-password`,
  },
  system: {
    home: `${SYSTEM}/`,
    health: `${SYSTEM}/health`,
  },
  game: {
    save: `${GAME}/save`,
    partySlot: (slotPosition: number) => `${GAME}/save/party/${slotPosition}`,
  },
  pokemon: {
    search: (query: string) => `${API_V1}/pokemon/${encodeURIComponent(query)}`,
  },
} as const;