"""Plantilla del juego Arkanoid para el hito M2 - COMPLETO."""
from arkanoid_core import *
from pathlib import Path
import random
@arkanoid_method
def cargar_nivel(self) -> list[str]:
    
        path = Path(self.level_path)
        
        if not path.exists():
            print(f"No se encuentra {path}")
        
        contenido = path.read_text(encoding="utf-8")
        filas = [linea for linea in contenido.splitlines() if linea.strip()]
        
        if not filas:
            raise ValueError("El fichero de nivel está vacío.")
        
        #comprobación de anchura con `len` que todas las filas tienen la misma longitud
        ancho_esperado = len(filas[0])
        for fila in filas:
            if len(fila) != ancho_esperado:
                raise ValueError("Las filas del fichero de nivel no tienen la misma longitud.")

        self.layout = filas
        return self.layout

@arkanoid_method
def preparar_entidades(self) -> None:
        self.paddle = self.crear_rect(0, 0, *self.PADDLE_SIZE)
        self.paddle.midbottom = (self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT - 30)   
        self.score = 0
        self.lives = 3
        self.end_message = ""
        self.reiniciar_bola()


@arkanoid_method
def crear_bloques(self) -> None:
        self.blocks = []
        self.block_colors = []
        self.block_symbols = []
        self.block_vida = []
        for fila, row_text in enumerate(self.layout):
            for columna, bloque in enumerate(row_text):
                if bloque == '.': continue

                bloque_rect = self.calcular_posicion_bloque(fila, columna)
                self.blocks.append(bloque_rect)
                self.block_symbols.append(bloque)
                

                if bloque == '#': 
                    self.block_colors.append((200, 200, 200))
                    self.block_vida.append(1)
                elif bloque == '@': 
                    self.block_colors.append((255, 50, 50))
                    self.block_vida.append(2)
                elif bloque == '%': 
                    self.block_colors.append((255, 215, 0))
                    self.block_vida.append(1)
                

@arkanoid_method
def procesar_input(self) -> None:
        if self.end_message: 
            return
        keys = self.obtener_estado_teclas()
        if keys[self.KEY_LEFT] or keys[self.KEY_A]:
            self.paddle.x -= self.PADDLE_SPEED
        if keys[self.KEY_RIGHT] or keys[self.KEY_D]:
            self.paddle.x += self.PADDLE_SPEED

        if self.paddle.left < 0: self.paddle.left = 0
        elif self.paddle.right > self.SCREEN_WIDTH: self.paddle.right = self.SCREEN_WIDTH

@arkanoid_method
@arkanoid_method
def actualizar_bola(self) -> None:
    if self.end_message: 
        return
    # Movimiento
    self.ball_pos += self.ball_velocity
    ball_rect = self.obtener_rect_bola()

    # Rebotes paredes
    if ball_rect.left <= 0:
        try: 
            if self.sfx_rebote: self.sfx_rebote.play()
        except: pass
        ball_rect.left = 0
        self.ball_velocity.x *= -1
    elif ball_rect.right >= self.SCREEN_WIDTH:
        try: 
            if self.sfx_rebote: self.sfx_rebote.play()
        except: pass
        ball_rect.right = self.SCREEN_WIDTH
        self.ball_velocity.x *= -1
    if ball_rect.top <= 0:
        try: 
            if self.sfx_rebote: self.sfx_rebote.play()
        except: pass
        ball_rect.top = 0
        self.ball_velocity.y *= -1

    # Suelo
    if ball_rect.bottom >= self.SCREEN_HEIGHT:
        self.lives -= 1
        if self.lives > 0: 
            self.reiniciar_bola()
        else: 
            try:
                if self.sfx_explosion: self.sfx_explosion.play()
            except: pass
            self.end_message = "GAME OVER"
        return

    # Paleta
    if ball_rect.colliderect(self.paddle):
        try:
            if self.sfx_rebote: self.sfx_rebote.play()
        except: pass
        self.ball_velocity.y *= -1
        ball_rect.bottom = self.paddle.top
        self.ball_pos.y = ball_rect.centery

    # Bloques
    bloque_chocado = ball_rect.collidelist(self.blocks)
    if bloque_chocado != -1:
        self.ball_velocity.y *= -1
        self.block_vida[bloque_chocado] -= 1
        if self.block_vida[bloque_chocado] <= 0:
            self.blocks.pop(bloque_chocado)
            self.block_colors.pop(bloque_chocado)
            self.block_vida.pop(bloque_chocado)
            simbolo = self.block_symbols.pop(bloque_chocado)
            if simbolo == '@': 
                self.score += 50
            elif simbolo == '%': 
                self.score += 100
            else: 
                self.score += 20
        else:
            try:
                if self.sfx_rebote: self.sfx_rebote.play()
            except: pass
            self.block_colors[bloque_chocado] = (255, 150, 150)

        if len(self.blocks) == 0:
            try:
                if self.sfx_victoria: self.sfx_victoria.play()
            except: pass
            self.end_message = "¡HAS GANADO!"
            self.dibujar_texto(self.end_message, (self.SCREEN_WIDTH//2 - 500, self.SCREEN_HEIGHT//2-275), grande=True)
            self.ball_velocity = Vector2(0, 0) 
            return

        self.ball_pos.x = ball_rect.centerx
        self.ball_pos.y = ball_rect.centery


"""-------------------------------------------------------------------------------------------------------"""
""" METODO reiniciar_bola MODIFICADO PARA QUE LA BOLA SALGA EN UNA DIRECCIÓN ALEATORIA AL REINICIARSE """
""" No queríamos modificar el core original, así que añadimos este método modificado aquí.
    Este método sobreescribe al método original definido en arkanoid_core.py
    HAY QUE PREGUNTARLE AL PROFESOR SI ESTO ESTÁ PERMITIDO. """
@arkanoid_method
def reiniciar_bola(self) -> None:
    self.ball_pos = Vector2(self.paddle.centerx, self.paddle.top - self.BALL_RADIUS)

    velocidad_x = random.choice([-5, -4, -3, 3, 4, 5])
        
    self.ball_velocity = Vector2(velocidad_x, -5)
        
    self.dibujar_escena()
    self.actualizar_pantalla()
    self.esperar(1500)
"""-------------------------------------------------------------------------------------------------------"""

@arkanoid_method
def dibujar_escena(self) -> None:
        self.screen.fill((40, 40, 30))
        
        for rect, color in zip(self.blocks, self.block_colors):
            self.dibujar_rectangulo(rect, color)
        self.dibujar_rectangulo(self.paddle, (255, 255, 255))
        self.dibujar_circulo(self.ball_pos, self.BALL_RADIUS, (255, 255, 0))
        self.dibujar_texto(f"Puntuación: {self.score}", (20, self.SCREEN_HEIGHT - 30))
        self.dibujar_texto(f"Vidas: {self.lives}", (700, self.SCREEN_HEIGHT - 30))

        if self.end_message:
            self.dibujar_texto(self.end_message, (self.SCREEN_WIDTH//2 - 100, self.SCREEN_HEIGHT//2-275), grande=True)

@arkanoid_method
def run(self) -> None:
    self.inicializar_pygame()

    self.sfx_rebote = None
    self.sfx_explosion = None
    self.sfx_victoria = None

    self.cargar_nivel()
    self.preparar_entidades()
    self.crear_bloques()
    running = True

    while running:
        for event in self.iterar_eventos():
            if event.type == self.EVENT_QUIT: running = False
            elif event.type == self.EVENT_KEYDOWN and event.key == self.KEY_ESCAPE: running = False

        self.procesar_input()
        self.actualizar_bola()
        self.dibujar_escena()
        self.actualizar_pantalla()
        self.clock.tick(self.FPS)

    self.finalizar_pygame()

# Bloque Main
def main() -> None:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("level", type=str, help="Ruta al fichero de nivel")
    args = parser.parse_args()
    
    game = ArkanoidGame(args.level)
    game.run()

if __name__ == "__main__":
    main()