import { backendClient } from '../http/client';
import { API_ROUTES } from '../apiRoutes';

export interface PartySlot {
  id: number;
  slot_position: number;
  trainer_pokemon_id: number;
}

export interface GameSave {
  id: number;
  trainer_id: number;
  map_id: string;
  tile_x: number;
  tile_y: number;
  direction: 'up' | 'down' | 'left' | 'right';
  money: number;
  play_time_seconds: number;
  badges: string[];
  inventory: Record<string, number>;
  game_flags: Record<string, boolean | string | number>;
  party_slots: PartySlot[];
  created_at: string | null;
  updated_at: string | null;
}

export interface GameSaveUpdate {
  map_id?: string;
  tile_x?: number;
  tile_y?: number;
  direction?: 'up' | 'down' | 'left' | 'right';
  money?: number;
  play_time_seconds?: number;
  badges?: string[];
  inventory?: Record<string, number>;
  game_flags?: Record<string, boolean | string | number>;
}

export const gameService = {
  /** Carga la partida guardada del entrenador autenticado. */
  loadSave: () =>
    backendClient.get<GameSave>(API_ROUTES.game.save).then((r) => r.data),

  /** Crea una nueva partida (solo si no existe). */
  newGame: () =>
    backendClient.post<GameSave>(API_ROUTES.game.save).then((r) => r.data),

  /** Autosave / manual save: actualiza estado de la partida. */
  saveGame: (payload: GameSaveUpdate) =>
    backendClient.put<GameSave>(API_ROUTES.game.save, payload).then((r) => r.data),

  /** Asigna un pokémon a un slot de la party (0-5). */
  setPartySlot: (slotPosition: number, trainerPokemonId: number) =>
    backendClient
      .post<GameSave>(API_ROUTES.game.partySlot(slotPosition), null, {
        params: { trainer_pokemon_id: trainerPokemonId },
      })
      .then((r) => r.data),

  /** Remueve el pokémon de un slot de la party. */
  removePartySlot: (slotPosition: number) =>
    backendClient
      .delete<GameSave>(API_ROUTES.game.partySlot(slotPosition))
      .then((r) => r.data),
};
