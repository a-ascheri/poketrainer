import Phaser from 'phaser';
import { useEffect, useRef } from 'react';
import { WorldScene } from '../scenes/WorldScene';

export interface DpadState {
  up: boolean;
  down: boolean;
  left: boolean;
  right: boolean;
  interact: boolean;
  blocked: boolean;
}

interface PhaserGameProps {
  width: number;
  height: number;
  initMapKey?: string;
  initTileX?: number;
  initTileY?: number;
  onSave?: (tileX: number, tileY: number, mapKey: string) => void;
  onInteract?: (message: string) => void;
  dpadState?: DpadState;
}

export default function PhaserGame({ width, height, initMapKey, initTileX, initTileY, onSave, onInteract, dpadState }: PhaserGameProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const gameRef = useRef<Phaser.Game | null>(null);
  const onSaveRef = useRef(onSave);
  useEffect(() => { onSaveRef.current = onSave; }, [onSave]);
  const onInteractRef = useRef(onInteract);
  useEffect(() => { onInteractRef.current = onInteract; }, [onInteract]);

  useEffect(() => {
    if (!containerRef.current || gameRef.current) return;

    gameRef.current = new Phaser.Game({
      type: Phaser.AUTO,
      width,
      height,
      backgroundColor: '#1a1a2e',
      parent: containerRef.current,
      scene: [],
      physics: {
        default: 'arcade',
        arcade: { debug: false },
      },
      input: {
        keyboard: {
          capture: []
        }
      },
      banner: false,
      callbacks: {
        postBoot: (game) => {
          game.scene.add('WorldScene', WorldScene, true, {
            mapKey: initMapKey ?? 'pine_town',
            tileX: initTileX ?? 5,
            tileY: initTileY ?? 7,
            onSave: (x: number, y: number, mk: string) => onSaveRef.current?.(x, y, mk),
            onInteract: (msg: string) => onInteractRef.current?.(msg),
            onOpenMenu: () => {
              // Simular el comportamiento de presionar Enter que teniamos en GameShell
              const event = new KeyboardEvent('keydown', { code: 'Enter', bubbles: true });
                   window.dispatchEvent(event);
            },
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

  // Apenas el canvas de Phaser esté en el DOM, le damos foco para que
  // reciba Space/Z/Enter sin necesitar un click previo del usuario.
  useEffect(() => {
    if (!containerRef.current) return;
    const observer = new MutationObserver(() => {
      const canvas = containerRef.current?.querySelector('canvas');
      if (canvas) {
        canvas.setAttribute('tabindex', '0');
        canvas.focus({ preventScroll: true });
        observer.disconnect();
      }
    });
    observer.observe(containerRef.current, { childList: true, subtree: true });
    return () => observer.disconnect();
  }, []);

  return <div ref={containerRef} style={{ lineHeight: 0 }} />;
}


