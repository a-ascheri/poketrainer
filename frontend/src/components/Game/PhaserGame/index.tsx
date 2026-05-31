import Phaser from 'phaser';
import { useEffect, useRef } from 'react';
import { WorldScene } from '../scenes/WorldScene';

export interface DpadState {
  up: boolean;
  down: boolean;
  left: boolean;
  right: boolean;
}

interface PhaserGameProps {
  width: number;
  height: number;
  initMapKey?: string;
  initTileX?: number;
  initTileY?: number;
  onSave?: (tileX: number, tileY: number, mapKey: string) => void;
  dpadState?: DpadState;
}

export default function PhaserGame({ width, height, initMapKey, initTileX, initTileY, onSave, dpadState }: PhaserGameProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const gameRef = useRef<Phaser.Game | null>(null);
  // Keep onSave up-to-date without restarting Phaser on each render
  const onSaveRef = useRef(onSave);
  useEffect(() => { onSaveRef.current = onSave; }, [onSave]);

  useEffect(() => {
    if (!containerRef.current || gameRef.current) return;

    gameRef.current = new Phaser.Game({
      type: Phaser.AUTO,
      width,
      height,
      backgroundColor: '#1a1a2e',
      parent: containerRef.current,
      // No scenes in array — we start manually via postBoot to pass init data
      scene: [],
      physics: {
        default: 'arcade',
        arcade: { debug: false },
      },
      banner: false,
      callbacks: {
        postBoot: (game) => {
          game.scene.add('WorldScene', WorldScene, true, {
            mapKey: initMapKey ?? 'pallet_town',
            tileX: initTileX ?? 5,
            tileY: initTileY ?? 7,
            onSave: (x: number, y: number, mk: string) => onSaveRef.current?.(x, y, mk),
            dpad: dpadState,
          });
        },
      },
    });

    return () => {
      gameRef.current?.destroy(true);
      gameRef.current = null;
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [width, height]);

  return <div ref={containerRef} style={{ lineHeight: 0 }} />;
}
