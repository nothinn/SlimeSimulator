import chisel3._
import chisel3.tester._
import org.scalatest.FreeSpec

class SlimeSpec extends FreeSpec with ChiselScalatestTester {

  "Slime should pass" in {
    test(new Slime) { dut =>

      dut.io.start.poke(1.B)
      dut.clock.step(1)
      dut.io.done.expect(1.B)

    }
  }
}