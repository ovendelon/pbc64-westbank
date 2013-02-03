from bge import logic , events
from mathutils import Vector, Euler, Matrix
import math , random

class Game:
	scene = logic.getCurrentScene()
	camera = scene.objects[ "Camera" ]
	scene.active_camera = camera
	logic.LibLoad( "//scene-lib/characters.blend" , "Scene" , load_actions=True )
	
	game_master = scene.objects["game_master"]
	kbd = game_master.sensors[ "Keyboard" ]
	
	def __init__( self ):
		self.rooms = []
		for ofs in [ -2 , 0 , 2 ]:
			self.rooms.append( Room( ofs ) )
			
	def main( self ):
		[ room.Run() for room in self.rooms ]
		if Game.kbd.positive:
			for key , status in Game.kbd.events:
				if key == events.ONEKEY and status == 1:
					self.rooms[ 0 ].Shoot( )
				if key == events.TWOKEY and status == 1:
					self.rooms[ 1 ].Shoot( )
				if key == events.THREEKEY and status == 1:
					self.rooms[ 2 ].Shoot( )
					
class Enemy:
	
	class Anim:
		def __init__( self , action , start , end ):
			self.action = action
			self.start = start
			self.end = end

	class AnimState:
		IDLE = 0
		DRAW = 1
		SHOOT = 2
		DIE = 3

	enm = Game.scene.objectsInactive[ "cowboy_armature" ]
	actions = [ Anim( "idle" , 1 , 120 ) , Anim( "draw" , 1 , 15 ) , Anim( "shoot" , 1 , 60 ) , Anim( "die" , 1 , 30 ) ]
	
	def __del__( self ):
		self.character.endObject()
	
	def __init__( self , offset ):
		self.character = Game.scene.addObject( Enemy.enm , Enemy.enm )
		self.character.worldPosition.x = offset
		self.character.worldPosition.y = 0.5
		
		self.wait_timer = random.randint( 1000 , 3000 )
		self.draw_timer = random.randint( 1000 , 3000 )
		self.shoot_timer = random.randint( 1000 , 3000 )
		self.Play( random.choice( [ Enemy.AnimState.IDLE , Enemy.AnimState.DRAW ] ) )
		self.isAlive = True

	def Play( self , state ):
		action = Enemy.actions[ state ]
		self.character.playAction( action.action , action.start , action.end )
		self.active_state = state
		print( "play %s" % state )
		
	def PlayFinished( self ):
		return not self.character.isPlayingAction()
	
	def CheckShootable( self ):
		return self.active_state == Enemy.AnimState.DRAW
	
	def Kill( self ):
		self.Play( Enemy.AnimState.DIE )
		self.isAlive = False
	
	def Run( self ):
		if not self.isAlive:
			if self.PlayFinished():
				return "dead"
			else:
				return "running"
		self.wait_timer -= logic.CONSTANT_TIMER
		if self.wait_timer < 0:
			if self.active_state == Enemy.AnimState.IDLE:
				self.draw_timer -= logic.CONSTANT_TIMER
				if self.draw_timer < 0:
					self.Play( Enemy.AnimState.DRAW )
			elif self.active_state == Enemy.AnimState.DRAW:
				self.shoot_timer -= logic.CONSTANT_TIMER
				if self.shoot_timer < 0:
					self.Play( Enemy.AnimState.SHOOT )
			elif self.active_state == Enemy.AnimState.SHOOT:
				if self.PlayFinished():
					return "has shot"
		return "running"
					
class Room:
	door = Game.scene.objectsInactive[ "door" ]
	room = Game.scene.objectsInactive[ "room" ]
	
	def __init__( self , offset ):
		self.offset = offset
		self.room = Game.scene.addObject( Room.room , Room.room )
		self.room.worldPosition.x = offset
		self.door = Game.scene.addObject( Room.door , Room.door )
		self.door.worldPosition.x = offset + 0.5
		self.ResetRoom()
		
	def ResetRoom( self ):
		self.isOpen = False
		self.wait_timer = random.randint( 1000 , 3000 )
		self.character = Enemy( self.offset )
		self.isActive = False
		self.CloseDoor()
	
	def OpenDoor( self ):
		self.door.worldOrientation = Euler( ( 0.0, 0.0 , math.radians( 90.0 ) ), 'XYZ')
		self.isOpen = True

	def CloseDoor( self ):
		self.door.worldOrientation = Euler( ( 0.0, 0.0 , math.radians(  0.0 ) ), 'XYZ')
		self.isOpen = False

	def Run( self ):
		self.wait_timer -= logic.CONSTANT_TIMER
		if self.wait_timer < 0:
			self.isActive = True
			self.OpenDoor()
			status = self.character.Run()
			if status != "running":
				self.ResetRoom()
				
	def Shoot( self ):
		if not self.isOpen:
			print( "miss" )
			return
		if self.character.CheckShootable( ):
			self.character.Kill( )
			return
		print( "Bang!" )
			
def main( cont ):
	owner = cont.owner
	if not "init" in owner:
		owner[ "class" ] = Game()
		owner[ "init" ] = True
	else:
		owner[ "class" ].main()
	
if __name__ == "__main__":
	pass