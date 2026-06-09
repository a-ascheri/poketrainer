import { backendClient } from '../http/client';
import { API_ROUTES } from '../apiRoutes';

export interface PokemonType {
  name: string;
}

export interface PokemonStat {
  name: string;
  value: number;
}

export interface PokemonMove {
  name: string;
  learnLevel: number;
}

export interface PokemonData {
  id: number;
  name: string;
  height: number;
  weight: number;
  imageUrl: string;
  officialArtwork: string;
  types: PokemonType[];
  abilities: string[];
  moves: PokemonMove[];
  evolutionChain: string[];
  stats: PokemonStat[];
}
export const searchPokemon = async (query: string): Promise<PokemonData> => {
  const response = await backendClient.get<PokemonData>(
    API_ROUTES.pokemon.search(query),
  );
  return response.data;
};
