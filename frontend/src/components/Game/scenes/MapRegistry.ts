/**
 * Central registry for all game maps.
 *
 * HOW TO ADD A NEW MAP
 * --------------------
 * 1. Create the Tiled JSON file in public/maps/<key>.json
 * 2. Add an entry to MAP_REGISTRY below.
 * 3. Add connections to/from adjacent maps.
 *
 * CONNECTION AXIS RULES
 * ----------------------
 * - top/bottom exits  → spawnY is the landing row; player X is preserved.
 * - left/right exits  → spawnX is the landing column; player Y is preserved.
 *
 * Make sure the exit tile in your map's objects layer is empty (value 0)
 * so the player can actually walk off the edge. All other border tiles
 * should be blocking (non-zero) to keep the player inside.
 *
 * FUTURE EXTENSION POINTS
 * -------------------------
 * - Add an `events` field per map for zone triggers / NPC interactions.
 * - Add a `music` field to play background music per area.
 * - Add `weather` or `lighting` flags for visual effects.
 */

export interface MapConnection {
  /** Key of the target map in MAP_REGISTRY. */
  targetMap: string;
  /**
   * Landing column (tile X) in the target map.
   * Only used for left/right exits; top/bottom exits preserve the player's current X.
   */
  spawnX: number;
  /**
   * Landing row (tile Y) in the target map.
   * Only used for top/bottom exits; left/right exits preserve the player's current Y.
   */
  spawnY: number;
}

export interface MapDef {
  key: string;
  label: string;
  jsonKey: string;
  jsonUrl: string;
  tilesetKey: string;
  tilesetUrl: string;
  tilesetKey2?: string;
  tilesetUrl2?: string;
  widthInTiles: number;
  heightInTiles: number;
  groundLayer: string;
  objectLayer: string;
  connections: {
    top?: MapConnection;
    bottom?: MapConnection;
    left?: MapConnection;
    right?: MapConnection;
  };
  signs?: Array<{ tileX: number; tileY: number; text: string }>;
}

export const MAP_REGISTRY: Record<string, MapDef> = {
  pine_town: {
    key: 'pine_town',
    label: 'Pine Town',
    jsonKey: 'map_pine_town',
    jsonUrl: '/maps/pine_town.json',
    tilesetKey: 'pokemonlike',
    tilesetUrl: '/tilesets/pokemonlike.png',
    tilesetKey2: 'tilemap',        // ← AGREGAR ESTO
    tilesetUrl2: '/tilesets/tilemap.png',  // ← AGREGAR ESTO, agregar mas referencias y agregarlas al worldscene para mas mapas
    widthInTiles: 40,
    heightInTiles: 40,
    groundLayer: 'ground',
    objectLayer: 'objects',
    connections: {
      // Walk off the top edge → Route 1 (player X is preserved, spawns near bottom)
      top: { targetMap: 'forest', spawnX: 0, spawnY: 57 },
    },
    signs: [
      { tileX: 25, tileY: 19, text: '¡Bienvenido a Pine Town!' },
    ],
  },

  forest: {
    key: 'forest',
    label: 'Forest',
    jsonKey: 'map_forest',
    jsonUrl: '/maps/forest.json',
    tilesetKey: 'pokemonlike',
    tilesetUrl: '/tilesets/pokemonlike.png',
    tilesetKey2: 'tilemap',        // ← AGREGAR ESTO
    tilesetUrl2: '/tilesets/tilemap.png',  // ← AGREGAR ESTO
    widthInTiles: 40,
    heightInTiles: 60,
    groundLayer: 'ground',
    objectLayer: 'objects',
    connections: {
      // Walk off the bottom edge → back to Pallet Town (player X is preserved)
      bottom: { targetMap: 'pine_town', spawnX: 0, spawnY: 2 },
    },
    // Los signs van definidos una posicion de un tile objeto, se sacan mediante metricas de posicion
    signs: [  
      { tileX: 8, tileY: 9, text: 'Wild Cave, el ingreso es bajo su propio riesgo' },
      { tileX: 24, tileY: 6, text: 'MasterCave-Center:\n\nCentro de estudio de los fenómenos físicos, anómalos de origen desconocido y espeleológicos de las cavernas profundas.' },
      { tileX: 33, tileY: 21, text: 'Residencia del Dr.Joe' },
    ],
  },

  cave: {
    key: 'cave', 
    label: 'Cueva',
    jsonKey: 'map_cave',
    jsonUrl: '/maps/cave.json',
    tilesetKey: 'pokemonlike',
    tilesetUrl: '/tilesets/pokemonlike.png',
    tilesetKey2: 'tilemap',
    tilesetUrl2: '/tilesets/tilemap.png',
    widthInTiles: 20,
    heightInTiles: 20,
    groundLayer: 'ground',
    objectLayer: 'objects',
    connections: {
      // La salida de la cueva irá a forest.json en la posición [7, 5]
      // (justo debajo de donde entramos)
      bottom: { targetMap: 'forest', spawnX: 7, spawnY: 5 },
    },
    signs: [
      { tileX: 10, tileY: 10, text: 'Cueva oscura... ¡ten cuidado!' },
    ],
  },

};

export const DEFAULT_MAP = 'pine_town';
