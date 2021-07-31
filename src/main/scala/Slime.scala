package Slimer

import chisel3._
import chisel3.util._
import chisel3.experimental.ChiselEnum


import chisel3.stage.ChiselStage

class Slime extends Module {
  val io = IO(new Bundle {
    val start = Input(Bool())
    val done = Output(Bool())


    val dataOut = Output(UInt(32.W))
    val dataIn = Input(UInt(32.W))
    val readAll = Input(Bool())
    val writeAll = Input(Bool())

  })

  val memSize = 1024


  object State extends ChiselEnum {
    val sIdle, sMemFlush, sDone = Value
  }

  val state = RegInit(State.sIdle)
  val memRW = Reg(Bool()) // 0 means R, 1 means W
  val memCounter = Counter(memSize)

  val mem = Mem(memSize,UInt(32.W))

  io.done := 0.B


  io.dataOut := RegNext(mem(memCounter.value))
  switch(state){
    is (State.sIdle){
      when(io.readAll){
        state := State.sMemFlush
        memRW := 0.B
      }
      when(io.writeAll){
        state := State.sMemFlush
        memRW := 1.B
      }
    }
    is (State.sMemFlush){
      when(memCounter.inc()){
        state := State.sDone
      }
      when(memRW){ //Write. Read is always done by counter
        mem(memCounter.value) := io.dataIn
      }
    }
    is (State.sDone){
      state := State.sIdle
      io.done := 1.B
    }
  }

  
}

// generate Verilog
object Slime extends App {
  (new ChiselStage).emitVerilog(
    new Slime,

    //args
    Array("--target-dir", "output/")
    )
}