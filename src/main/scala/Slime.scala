import chisel3._
import chisel3.util._

import chisel3.stage.ChiselStage

class Slime extends Module {
  val io = IO(new Bundle {
    val start = Input(Bool())
    val done = Output(Bool())
  })

  io.done := RegNext (io.start)
}

// generate Verilog
object Slime extends App {
  (new ChiselStage).emitVerilog(
    new Slime,

    //args
    Array("--target-dir", "output/")
    )
}