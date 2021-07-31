package Slimer

import chisel3._
import chisel3.tester._
import org.scalatest.FreeSpec

import chiseltest.experimental.TestOptionBuilder._
import chiseltest.internal.{VerilatorBackendAnnotation, WriteVcdAnnotation}


import java.nio.file.{Files, Paths}
import java.io._

class SlimeSpec extends FreeSpec with ChiselScalatestTester {

  "Slime should pass" in {
    val args = Array("--backend-name", "firrtl", "--fint-write-vcd")
    test(new Slime).withAnnotations(Seq(WriteVcdAnnotation))
    { dut =>
      dut.clock.setTimeout(2000 + 4)


      dut.io.writeAll.poke(1.B)
      dut.clock.step(1)
      dut.io.writeAll.poke(0.B)
      for(i <- 1000 until 2024){
        dut.io.dataIn.poke(i.U)
        dut.clock.step(1)
      }
      dut.clock.step(100)

      dut.io.readAll.poke(1.B)
      dut.clock.step(1)
      dut.io.readAll.poke(0.B)
      while(dut.io.done.peek.litValue.toInt == 0){
        println(dut.io.dataOut.peek)
        dut.clock.step(1)
      }
      println(dut.io.dataOut.peek)
      
      dut.io.done.expect(1.B)
      dut.clock.step(1)
    }
  }



  "Slime should read file and write same file" in {
    val args = Array("--backend-name", "firrtl", "--fint-write-vcd")
    test(new Slime).withAnnotations(Seq(WriteVcdAnnotation))
    { dut =>
      dut.clock.setTimeout(2000 + 4)

      dut.io.writeAll.poke(1.B)
      dut.clock.step(1)
      dut.io.writeAll.poke(0.B)
      val byteArray = Files.readAllBytes(Paths.get("testFile.bin"))
      for(i <- 0 until byteArray.size by 4){
        var value = byteArray(i).toLong & 0xff
        value = (value << 8) + (byteArray(i+1).toLong & 0xff)
        value = (value << 8) + (byteArray(i+2).toLong & 0xff)
        value = (value << 8) + (byteArray(i+3).toLong & 0xff)
        dut.io.dataIn.poke(value.U)
        dut.clock.step(1)
      }
      dut.clock.step(100)

      dut.io.readAll.poke(1.B)
      dut.clock.step(1)
      dut.io.readAll.poke(0.B)
      var fos = new FileOutputStream("testFileCopy.bin")
      for(i <- 0 until byteArray.size by 4){
        dut.clock.step(1)
        var value = byteArray(i).toLong & 0xff
        value = (value << 8) + (byteArray(i+1).toLong & 0xff)
        value = (value << 8) + (byteArray(i+2).toLong & 0xff)
        value = (value << 8) + (byteArray(i+3).toLong & 0xff)
        dut.io.dataOut.expect(value.U)
        var word = dut.io.dataOut.peek.litValue.toLong
        fos.write(word.toInt>>24 & 0xff)
        fos.write(word.toInt>>16 & 0xff)
        fos.write(word.toInt>>8 & 0xff)
        fos.write(word.toInt & 0xff)
      }
      fos.close()
      dut.io.done.expect(1.B)
      dut.clock.step(1)
    }
  }

/*
  "Memory should be filled with 0-1024 to all and save a file" in {
    val args = Array("--backend-name", "firrtl", "--fint-write-vcd")
    test(new Slime).withAnnotations(Seq(WriteVcdAnnotation))
    { dut =>

      val mem = Mem(1024,UInt(32.W))

      for(i <- 0 until 1024){
        mem(i) := i.U
      }


      for(i <- 0 until 1024){
        println(i)
      }
      
      dut.io.start.poke(1.B)
      dut.clock.step(1)
      dut.io.done.expect(1.B)
    }
  }
  */
}