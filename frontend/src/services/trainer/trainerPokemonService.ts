import { backendClient } from '../http/client';
import { API_ROUTES } from '../apiRoutes';

export interface StarterOption {
  id: number;
  name: string;
  types: string[];
}

export interface OwnedPokemon {
  id: number;
  trainer_id: number;
  pokemon: {
    id: number;
    pokeapi_id: number;
    name: string;
    types: string[];
    abilities: string[];
    base_stats: Record<string, number>;
    moves: Array<{ name: string; learn_level: number }>;
    evolution_chain?: { names?: string[] };
  };
  is_starter: boolean;
  current_level: number;
  current_experience: number;
  current_hp: number;
  max_hp: number;
  attack: number;
  defense: number;
  sp_attack: number;
  sp_defense: number;
  speed: number;
  known_moves: Array<{ name: string; learn_level: number }>;
}

export interface PokemonStats {
  trainer_pokemon_id: number;
  pokemon_name: string;
  current_level: number;
  current_experience: number;
  current_hp: number;
  max_hp: number;
  attack: number;
  defense: number;
  sp_attack: number;
  sp_defense: number;
  speed: number;
}

export interface PokemonMoves {
  trainer_pokemon_id: number;
  pokemon_name: string;
  current_level: number;
  known_moves: Array<{ name: string; learn_level: number }>;
}

export const getStarterOptions = async (): Promise<StarterOption[]> => {
  const response = await backendClient.get<StarterOption[]>(API_ROUTES.trainer.starterOptions);
  return response.data;
};

export const selectStarter = async (pokemonName: string): Promise<OwnedPokemon> => {
  const response = await backendClient.post<OwnedPokemon>(API_ROUTES.trainer.starterSelect, {
    pokemon_name: pokemonName,
  });
  return response.data;
};

export const gainPokemonExperience = async (
  trainerPokemonId: number,
  amount: number,
): Promise<OwnedPokemon> => {
  const response = await backendClient.post<OwnedPokemon>(API_ROUTES.trainer.gainExperience(trainerPokemonId), { amount });
  return response.data;
};

export const getPokemonStats = async (
  trainerPokemonId: number,
): Promise<PokemonStats> => {
  const response = await backendClient.get<PokemonStats>(API_ROUTES.trainer.pokemonStats(trainerPokemonId));
  return response.data;
};

export const getPokemonMoves = async (
  trainerPokemonId: number,
): Promise<PokemonMoves> => {
  const response = await backendClient.get<PokemonMoves>(API_ROUTES.trainer.pokemonMoves(trainerPokemonId));
  return response.data;
};
